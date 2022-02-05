from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_uploads import UploadSet, IMAGES
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import current_app

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail(current_app)
image_set = UploadSet('images', IMAGES)
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
