from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.recipe import Recipe
from flask_jwt_extended import get_jwt_identity, jwt_required
from schemas.recipe import RecipeSchema, RecipePaginationSchema
from utils import save_image
from extensions import image_set, cache, limiter
import os
from webargs.flaskparser import use_kwargs
from webargs import fields
from utils import clear_cache


recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)
recipe_cover_schema = RecipeSchema(only=('cover_image_url',))
recipe_pagination_schema = RecipePaginationSchema()


class RecipeListResource(Resource):
    decorators = [limiter.limit('3 per minute;30 per hour; 300 per day', methods=[
                                'GET'], error_message='Too Many Requests')]

    @use_kwargs({'q': fields.Str(missing=''), 'page': fields.Int(missing=1),
                 'per_page': fields.Int(missing=20), 'sort': fields.Str(missing='created_at'),
                 'order': fields.Str(missing='desc')}, location='query')
    @cache.cached(timeout=300, key_prefix='/recipes', query_string=True)
    def get(self, q, page, per_page, sort, order):
        if order not in ['asc', 'desc']:
            order = 'desc'
        if sort not in ['created_at', 'cook_time', 'no_of_servings']:
            sort = 'created_at'
        paginated_recipes = Recipe.get_all_published(q=q,
                                                     page=page, per_page=per_page, sort=sort, order=order)
        # print("querying database...")
        return recipe_pagination_schema.dump(paginated_recipes), HTTPStatus.OK

    @jwt_required()
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()
        data = recipe_schema.load(data=json_data)

        recipe = Recipe(**data)
        recipe.user_id = current_user
        recipe.save()

        return recipe_schema.dump(recipe), HTTPStatus.CREATED


class RecipeResource(Resource):
    @ jwt_required()
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.is_publish == False and recipe.user_id != current_user:
            return {'message': 'Access not allowed'}, HTTPStatus.FORBIDDEN
        return recipe_schema.dump(recipe), HTTPStatus.OK

    @ jwt_required(optional=False)
    def put(self, recipe_id):
        data = request.get_json()
        recipe = Recipe.get_by_id(id=recipe_id)
        if recipe == None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.user_id != current_user:
            return {'message': 'Access not allowed'}, HTTPStatus.FORBIDDEN
        recipe.name = data.get('name')
        recipe.description = data.get('description')
        recipe.no_of_servings = data.get('no_of_servings')
        recipe.cook_time = data.get('cook_time')
        recipe.directions = data.get('directions')
        recipe.save()
        clear_cache('api/recipes')
        return recipe.data(), HTTPStatus.OK

    @jwt_required()
    def patch(self, recipe_id):
        json_data = request.get_json()
        data = recipe_schema.load(data=json_data, partial=('name',))
        recipe = Recipe.get_by_id(recipe_id)
        if recipe == None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.user_id != current_user:
            return {"message": "method not allowed"}, HTTPStatus.FORBIDDEN
        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.ingredients = data.get('ingredients') or recipe.ingredients
        recipe.no_of_servings = data.get(
            'no_of_servings') or recipe.no_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.directions = data.get('directions') or recipe.directions

        recipe.save()
        clear_cache('api/recipes')
        return recipe_schema.dump(recipe), HTTPStatus.OK

    @ jwt_required
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe == None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.user_id != current_user:
            return {"message": "access not allowed"}, HTTPStatus.FORBIDDEN
        recipe.delete()
        return {}, HTTPStatus.NO_CONTENT


class RecipePublishResource(Resource):
    @ jwt_required()
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe == None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.user_id != current_user:
            return {"message": "access not allowed"}, HTTPStatus.FORBIDDEN
        recipe.is_publish = True
        recipe.save()
        clear_cache('api/recipes')
        return {}, HTTPStatus.NO_CONTENT

    @ jwt_required()
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe == None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.user_id != current_user:
            return {"message": "access not allowed"}, HTTPStatus.FORBIDDEN
        recipe.is_publish = False
        clear_cache('api/recipes')
        return {}, HTTPStatus.NO_CONTENT


class RecipeCoverUploadResource(Resource):
    @jwt_required()
    def put(self, recipe_id):
        file = request.files.get('cover')
        if not file:
            return {"message": "invalid file"}, HTTPStatus.BAD_REQUEST
        if not image_set.file_allowed(file, file.filename):
            return {"message": "invalid file extension"}, HTTPStatus.BAD_REQUEST
        recipe = Recipe.get_by_id(recipe_id)
        current_user = get_jwt_identity()
        if recipe.user_id != current_user:
            return {"message": "access not allowed"}, HTTPStatus.FORBIDDEN
        if recipe.cover_image:
            cover_path = image_set.path(
                folder='recipes', filename=recipe.cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)
        filename = save_image(image=file, folder='recipes')
        recipe.cover_image = filename
        recipe.save()
        clear_cache('api/recipes')
        return recipe_cover_schema.dump(recipe), HTTPStatus.OK
