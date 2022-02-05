from flask import request, url_for
from flask_restful import Resource
from http import HTTPStatus
from utils import hash_password
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from schemas.user import UserSchema
from schemas.recipe import RecipeSchema, RecipePaginationSchema
from models.recipe import Recipe
from webargs import fields
from webargs.flaskparser import use_kwargs
from extensions import mail, image_set
from utils import generate_token, verify_token, save_image
from flask_mail import Message
import os
# globals
user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email',))
recipe_list_schema = RecipeSchema(many=True)
user_avatar_schema = UserSchema(only=('avatar_url',))
recipe_pagination_schema = RecipePaginationSchema()


class MeResource(Resource):
    @jwt_required(optional=True)
    def get(self):
        current_user = get_jwt_identity()
        user = User.get_by_id(id=current_user)
        return user_schema.dump(user), HTTPStatus.OK


class UserResource(Resource):
    @jwt_required(optional=True)
    def get(self, username):
        user = User.get_by_username(username=username)
        if user is None:
            return {'message': 'user not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user == user.id:
            return user_schema.dump(user), HTTPStatus.OK
        else:
            return user_public_schema.dump(user), HTTPStatus.OK


class UserListResource(Resource):
    def post(self):
        json_data = request.get_json()
        data = user_schema.load(data=json_data)

        username = data.get('username')
        email = data.get('email')

        if User.get_by_username(username):
            return {'message': 'username already exists'}, HTTPStatus.BAD_REQUEST
        if User.get_by_email(email):
            return {'message': 'email already exists'}, HTTPStatus.BAD_REQUEST

        user = User(**data)
        user.save()
        token = generate_token(user.email, salt='activate')
        subject = 'Please confirm your registration.'
        link = url_for('useractivateresource',
                       token=token,
                       _external=True)
        body = 'Hi, Thanks for using SmileCook! Please confirm your registration by clicking on the link: {}'.format(
            link)
        msg = Message(recipients=[user.email],
                      body=body,
                      subject=subject)
        mail.send(msg)
        return user_schema.dump(user), HTTPStatus.CREATED


class UserRecipeListResource(Resource):
    @jwt_required(optional=True)
    @use_kwargs({'page': fields.Int(missing=1), 'per_page': fields.Int(missing=10), 'visibility': fields.Str(missing='public')}, location='query')
    def get(self, username, page, per_page, visibility):
        user = User.get_by_username(username=username)
        if user == None:
            return {'message': 'No such user'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user == user.id and visibility in ['all', 'private']:
            pass
        else:
            visibility = 'public'

        paginated_recipes = Recipe.get_all_by_user(
            user_id=user.id, page=page, per_page=per_page, visibility=visibility)
        return recipe_pagination_schema.dump(paginated_recipes), HTTPStatus.OK


class UserActivateResource(Resource):
    def get(self, token):
        email = verify_token(token, salt='activate')
        if email is False:
            return {'message': 'Invalid tooken or token expired'}, HTTPStatus.BAD_REQUEST
        user = User.get_by_email(email)
        if not user:
            return {'message': 'Invalid user'}, HTTPStatus.NOT_FOUND
        if user.is_active == True:
            return {'message': 'user already active'}, HTTPStatus.BAD_REQUEST
        user.is_active = True
        user.save()
        return {'message': 'User activated'}, HTTPStatus.NO_CONTENT


class UserAvatarUploadResource(Resource):
    @jwt_required()
    def put(self):
        file = request.files.get('avatar')
        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST
        user = User.get_by_id(id=get_jwt_identity())
        if user.avatar_image:
            avatar_path = image_set.path(
                folder='avatars', filename=user.avatar_image)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
        filename = save_image(image=file, folder='avatars')
        user.avatar_image = filename
        user.save()
        return user_avatar_schema.dump(user), HTTPStatus.OK
