from core.factory import create_app
from config import config_by_name
import os
from api import operation
from flask_cors import CORS

environment = os.getenv('FLASK_ENV', 'dev')

app = create_app(config_by_name[environment])
# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",  # Your frontend development server
            "http://localhost:5173",  # Vite's default port
        ]
    }
})

app.register_blueprint(operation.bp, url_prefix='/api/operations')

if __name__ == '__main__':
    app.run(debug=True)