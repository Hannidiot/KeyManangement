from flask import Flask
from extensions import db
from flasgger import Swagger
from api.rsa import bp as keys_bp

def create_app(config_object):
    app = Flask(__name__)
    
    configure_app(app, config_object)
    configure_extensions(app)
    register_blueprints(app)
    configure_swagger(app)
    initialize_database(app)
    configure_logging(app)
    register_error_handlers(app)
    
    return app

def configure_app(app, config_object):
    app.config.from_object(config_object)

def configure_extensions(app):
    # Initialize Flask extensions
    db.init_app(app)

def configure_swagger(app):
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'swagger',
                "route": '/swagger.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/swagger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/"
    }

    template = {
        "swagger": "2.0",
        "info": {
            "title": "Flask API",
            "description": "API documentation using Flasgger",
            "version": "1.0.0"
        },
        "basePath": "/api",
        # "securityDefinitions": {
        #     "Bearer": {
        #         "type": "apiKey",
        #         "name": "Authorization",
        #         "in": "header",
        #         "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
        #     }
        # },
        # "security": [
        #     {
        #         "Bearer": []
        #     }
        # ]
    }

    Swagger(app, config=swagger_config, template=template)

def register_blueprints(app):
    # Register blueprints with URL prefix
    app.register_blueprint(keys_bp, url_prefix='/api/keys')

def initialize_database(app):
    with app.app_context():
        db.create_all()

def configure_logging(app):
    import logging
    logging.basicConfig(level=app.config.get('LOG_LEVEL', 'INFO'))

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error'}, 500