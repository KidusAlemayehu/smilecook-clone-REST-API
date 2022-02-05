from flask import request
from http import HTTPStatus
from flask_restful import Resource
from utils import check_password
from models.user import User
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required, get_jwt_identity,
                                get_jwt)


class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = User.get_by_email(email=email)
        if not user or not check_password(password, user.password):
            return {'message': 'email or password incorrect.'}, HTTPStatus.UNAUTHORIZED
        if user.is_active is False:
            return {'message': 'The user account is not activated yet'}, HTTPStatus.FORBIDDEN
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {'access_token': access_token, 'refresh_token': refresh_token}, HTTPStatus.OK


class RefreshTokenResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': access_token}, HTTPStatus.OK


'''in memory storage for storing blocked or revoked tokens'''
black_list = set()


class UserLogoutResource(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        black_list.add(jti)
        return {'message': 'successfully logged out'}, HTTPStatus.OK
