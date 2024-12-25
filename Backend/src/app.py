from core.factory import create_app
from config import config_by_name
import os
from api import operation

environment = os.getenv('FLASK_ENV', 'dev')

app = create_app(config_by_name[environment])

app.register_blueprint(operation.bp, url_prefix='/api/operations')

if __name__ == '__main__':
    app.run(debug=True)