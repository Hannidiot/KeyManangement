from core.factory import create_app
from config import config_by_name
import os

environment = os.getenv('FLASK_ENV', 'dev')

app = create_app(config_by_name[environment])

if __name__ == '__main__':
    app.run(debug=True)