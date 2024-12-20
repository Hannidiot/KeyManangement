from flask import Blueprint, jsonify, request, send_file
from models import Secret, RSASecretContent, SecretTypeModel, db
from http import HTTPStatus
from datetime import datetime, UTC
import io
import zipfile

bp = Blueprint('secret', __name__)

@bp.route('', methods=['POST'])
def create_secret():
    """
    Create a new secret
    ---
    tags:
      - secret
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - description
            - created_by
            - project_id
            - secret_type_id
          properties:
            description:
              type: string
              example: "RSA key pair for authentication"
            created_by:
              type: string
              example: "john.doe"
            project_id:
              type: integer
              example: 1
            secret_type_id:
              type: integer
              example: 1
            key_size:
              type: integer
              example: 2048
    responses:
      201:
        description: Secret created successfully
      400:
        description: Invalid request data
    """
    data = request.get_json()
    
    required_fields = ['description', 'created_by', 'project_id', 'secret_type_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST
    
    # Create the secret
    secret = Secret(
        description=data['description'],
        created_by=data['created_by'],
        project_id=data['project_id'],
        secret_type_id=data['secret_type_id'],
        created_at=datetime.now(UTC)
    )
    
    db.session.add(secret)
    
    # If it's an RSA secret, generate the key pair
    if data['secret_type_id'] == 1:  # Assuming 1 is RSA type
        from api.rsa import generate_rsa_key_pair
        private_pem, public_pem = generate_rsa_key_pair()
        
        rsa_content = RSASecretContent(
            private_key=private_pem,
            public_key=public_pem,
            key_size=data.get('key_size', 2048)
        )
        db.session.add(rsa_content)
        db.session.flush()  # Get the ID of rsa_content
        secret.rsa_content_id = rsa_content.id
    
    db.session.commit()
    
    return jsonify({
        'id': secret.id,
        'description': secret.description,
        'created_by': secret.created_by,
        'created_at': secret.created_at.isoformat(),
        'project_id': secret.project_id,
        'secret_type_id': secret.secret_type_id
    }), HTTPStatus.CREATED

@bp.route('', methods=['GET'])
def list_secrets():
    """
    List all secrets
    ---
    tags:
      - secret
    parameters:
      - name: project_id
        in: query
        type: integer
        required: false
        description: Filter secrets by project ID
    responses:
      200:
        description: List of secrets
    """
    project_id = request.args.get('project_id', type=int)
    query = Secret.query
    
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    secrets = query.all()
    return jsonify([{
        'id': s.id,
        'description': s.description,
        'created_by': s.created_by,
        'created_at': s.created_at.isoformat(),
        'project_id': s.project_id,
        'secret_type_id': s.secret_type_id
    } for s in secrets]), HTTPStatus.OK

@bp.route('/<int:secret_id>', methods=['GET'])
def get_secret(secret_id):
    """
    Get a specific secret
    ---
    tags:
      - secret
    parameters:
      - name: secret_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Secret details
      404:
        description: Secret not found
    """
    secret = Secret.query.get_or_404(secret_id)
    return jsonify({
        'id': secret.id,
        'description': secret.description,
        'created_by': secret.created_by,
        'created_at': secret.created_at.isoformat(),
        'project_id': secret.project_id,
        'secret_type_id': secret.secret_type_id
    }), HTTPStatus.OK

@bp.route('/<int:secret_id>', methods=['PUT'])
def update_secret(secret_id):
    """
    Update a secret
    ---
    tags:
      - secret
    parameters:
      - name: secret_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            description:
              type: string
    responses:
      200:
        description: Secret updated successfully
      404:
        description: Secret not found
    """
    secret = Secret.query.get_or_404(secret_id)
    data = request.get_json()
    
    if 'description' in data:
        secret.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'id': secret.id,
        'description': secret.description,
        'created_by': secret.created_by,
        'created_at': secret.created_at.isoformat(),
        'project_id': secret.project_id,
        'secret_type_id': secret.secret_type_id
    }), HTTPStatus.OK

@bp.route('/<int:secret_id>', methods=['DELETE'])
def delete_secret(secret_id):
    """
    Delete a secret
    ---
    tags:
      - secret
    parameters:
      - name: secret_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Secret deleted successfully
      404:
        description: Secret not found
    """
    secret = Secret.query.get_or_404(secret_id)
    
    # Delete associated RSA content if exists
    if secret.rsa_content:
        db.session.delete(secret.rsa_content)
    
    db.session.delete(secret)
    db.session.commit()
    
    return '', HTTPStatus.NO_CONTENT

@bp.route('/<int:secret_id>/download', methods=['GET'])
def download_secret(secret_id):
    """
    Download secret content
    ---
    tags:
      - secret
    parameters:
      - name: secret_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Returns a ZIP file containing the secret content
        content:
          application/zip:
            schema:
              type: string
              format: binary
      404:
        description: Secret not found or no content available
    """
    secret = Secret.query.get_or_404(secret_id)
    
    if not secret.rsa_content:
        return jsonify({'error': 'No RSA content available for this secret'}), HTTPStatus.NOT_FOUND
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('public_key.pem', secret.rsa_content.public_key)
        zf.writestr('private_key.pem', secret.rsa_content.private_key)
        
        # Add metadata file
        metadata = f"""Secret ID: {secret.id}
Description: {secret.description}
Created By: {secret.created_by}
Created At: {secret.created_at}
Key Size: {secret.rsa_content.key_size} bits
"""
        zf.writestr('metadata.txt', metadata)
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'secret_{secret_id}.zip'
    ) 