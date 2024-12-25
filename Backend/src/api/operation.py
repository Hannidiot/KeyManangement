from flask import Blueprint, jsonify
from models import UserOperation
from http import HTTPStatus

bp = Blueprint('operation', __name__)

@bp.route('', methods=['GET'])
def list_operations():
    """
    List all user operations
    ---
    tags:
      - operation
    responses:
      200:
        description: List of user operations
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              username:
                type: string
              operation:
                type: string
              timestamp:
                type: string
                format: date-time
              details:
                type: string
    """
    operations = UserOperation.query.order_by(UserOperation.timestamp.desc()).all()
    return jsonify([{
        'id': op.id,
        'username': op.username,
        'operation': op.operation,
        'timestamp': op.timestamp.isoformat(),
        'details': op.details
    } for op in operations]), HTTPStatus.OK 