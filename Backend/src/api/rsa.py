from flask import Blueprint, jsonify, send_file
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import io
import zipfile

from models import RSASecretContent
from extensions import db

bp = Blueprint('rsa_key', __name__)

@bp.route('/generate', methods=['POST'])
def generate():
    """
    Generate RSA Key Pair
    ---
    tags:
      - rsa_key
    responses:
      201:
        description: RSA key pair generated successfully
        schema:
          properties:
            message:
              type: string
              example: RSA key pair generated and stored successfully.
            public_key:
              type: string
      500:
        description: Internal server error
    """
    private_pem, public_pem = generate_rsa_key_pair()
    store_rsa_keys(private_pem, public_pem)
    return jsonify({
        'message': 'RSA key pair generated and stored successfully.',
        'public_key': public_pem
    }), 201

@bp.route('/<int:id>/public_key', methods=['GET'])
def get_public_key(id):
    """
    Get Public Key
    ---
    tags:
      - rsa_key
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the user
    responses:
      200:
        description: Public key retrieved successfully
        schema:
          properties:
            public_key:
              type: string
      404:
        description: Key pair not found
        schema:
          properties:
            error:
              type: string
              example: Key pair not found for the given user ID.
    """
    key_pair = RSASecretContent.query.filter_by(id=id).first()
    if key_pair:
        return jsonify({
            'public_key': key_pair.public_key
        }), 200
    else:
        return jsonify({'error': 'Key pair not found for the given user ID.'}), 404

@bp.route('/<int:id>/download', methods=['GET'])
def download_keys(id):
    """
    Download RSA Key Pair
    ---
    tags:
      - rsa_key
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the user
    responses:
      200:
        description: Returns a ZIP file containing the public and private rsa_key
        content:
          application/zip:
            schema:
              type: string
              format: binary
      404:
        description: Key pair not found
        schema:
          properties:
            error:
              type: string
              example: Key pair not found for the given user ID.
    """
    key_pair = RSASecretContent.query.filter_by(id=id).first()
    if not key_pair:
        return jsonify({'error': 'Key pair not found for the given user ID.'}), 404
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('public_key.pem', key_pair.public_key)
        zf.writestr('private_key.pem', key_pair.private_key)
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'rsa_keys_user_{id}.zip'
    )

def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_pem, public_pem

def store_rsa_keys(private_pem, public_pem):
    existing_keys = RSASecretContent.query.filter_by().first()
    if existing_keys:
        existing_keys.private_key = private_pem
        existing_keys.public_key = public_pem
    else:
        new_key_pair = RSASecretContent(
            private_key=private_pem,
            public_key=public_pem
        )
        db.session.add(new_key_pair)
    db.session.commit()