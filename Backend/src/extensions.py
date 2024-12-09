from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flasgger import Swagger

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
swagger = Swagger()