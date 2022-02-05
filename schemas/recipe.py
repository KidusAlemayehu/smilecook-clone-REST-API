from marshmallow import Schema, fields, validate, validates, ValidationError, post_dump
from schemas.user import UserSchema
from schemas.pagination import PaginationSchema
from flask import url_for


def validate_num_of_servings(n):
    if n < 1:
        raise ValidationError('value must be greater than 1')
    if n > 50:
        raise ValidationError('value must not be greater than 50')


class RecipeSchema(Schema):
    class Meta():
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(validate=[validate.Length(max=200)])
    ingredients = fields.String(validate=[validate.Length(max=1000)])
    cover_image_url = fields.Method(serialize='dump_cover_url')
    no_of_servings = fields.Integer(validate=validate_num_of_servings)
    cook_time = fields.Integer()
    directions = fields.String(validate=validate.Length(max=1000))
    is_publish = fields.Boolean(dump_only=True)
    author = fields.Nested(UserSchema, attribute='user',
                           dump_only=True, exclude=['email'])
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('cook_time')
    def validate_cook_time(self, value):
        if value < 1:
            raise ValidationError('value must be greater than 1')
        elif value > 300:
            raise ValidationError('value must not be greater than 300')

    def dump_cover_url(self, recipe):
        if recipe.cover_image:
            return url_for('static', filename='images/recipes/{}'.format(recipe.cover_image), _external=True)
        else:
            return url_for('static', filename='images/assets/default-recipe.jpg', _external=True)


class RecipePaginationSchema(PaginationSchema):
    data = fields.Nested(RecipeSchema, attribute='items', many=True)
