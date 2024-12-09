from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    current_user,
    get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, TokenBlocklist
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: The user's username
            password:
              type: string
              description: The user's password
          required:
            - username
            - password
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: User created successfully
      400:
        description: Invalid input
    """
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@bp.route('/login', methods=['POST'])
def login():
    """
    Login to get access token
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: The user's username
            password:
              type: string
              description: The user's password
          required:
            - username
            - password
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: JWT access token
            message:
              type: string
              example: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token, message="Login successful")

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout current user
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Successfully logged out
        schema:
          type: object
          properties:
            message:
              type: string
              example: Token revoked successfully
    """
    jwt = get_jwt()
    jti = jwt["jti"]
    user_id = current_user.id
    
    # Store the token in the blocklist
    token_block = TokenBlocklist(
        jti=jti,
        user_id=user_id,
        created_at=datetime.utcnow()
    )
    db.session.add(token_block)
    db.session.commit()
    
    return jsonify({
        "message": "Token revoked successfully",
        "token_id": jti
    })

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            old_password:
              type: string
              description: Current password
            new_password:
              type: string
              description: New password
          required:
            - old_password
            - new_password
    responses:
      200:
        description: Password changed successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Password changed successfully
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    user = User.query.get(current_user.id)
    if not user or not check_password_hash(user.password, data['old_password']):
        return jsonify({"message": "Invalid credentials"}), 401
    
    user.password = generate_password_hash(data['new_password'])
    db.session.commit()
    return jsonify({"message": "Password changed successfully"})

