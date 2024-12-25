from functools import wraps
from flask import request, g
from models import UserOperation, db
import json

def log_operation(operation_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the original function
            response = f(*args, **kwargs)
            
            try:
                # Get user_id from request (assuming it's in the created_by field)
                data = request.get_json() or {}
                username = data.get('created_by', 'anonymous')
                
                # Prepare details
                details = {
                    'url': request.url,
                    'method': request.method,
                    'params': dict(request.args),
                    'body': data,
                    'resource_id': kwargs.get('project_id') or kwargs.get('secret_id')
                }
                
                # Create operation record
                operation = UserOperation(
                    username=username,
                    operation=operation_type,
                    details=json.dumps(details)
                )
                
                db.session.add(operation)
                db.session.commit()
                
            except Exception as e:
                # Log the error but don't affect the original response
                print(f"Error logging operation: {str(e)}")
                
            return response
        return decorated_function
    return decorator 