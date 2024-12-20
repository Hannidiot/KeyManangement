from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

# Initialize extensions
db = SQLAlchemy()
swagger = Swagger()