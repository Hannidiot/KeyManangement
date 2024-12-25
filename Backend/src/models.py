from datetime import datetime, UTC
from extensions import db
from metadata import SecretType

class Project(db.Model):
    """Table to store projects that organize secrets"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    
    # Relationship with secrets
    secrets = db.relationship('Secret', backref='project', lazy=True)
    
    def __repr__(self):
        return f'<Project id={self.id} name={self.project_name}>'

class Secret(db.Model):
    """Main table to store secret metadata"""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    secret_type_id = db.Column(db.Integer, db.ForeignKey('secret_types.id'), nullable=False)
    
    # Add project foreign key
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Foreign keys to different content tables
    rsa_content_id = db.Column(db.Integer, db.ForeignKey('rsa_secret_content.id'))
    aes_content_id = db.Column(db.Integer, db.ForeignKey('aes_secret_content.id'))
    
    # Relationships
    rsa_content = db.relationship('RSASecretContent', backref='secret')
    aes_content = db.relationship('AESSecretContent', backref='secret')
    secret_type = db.relationship('SecretTypeModel', backref='secrets')

    def __repr__(self):
        return f'<Secret id={self.id} type={self.secret_type.name}>'

class RSASecretContent(db.Model):
    """Table to store RSA-specific content"""
    id = db.Column(db.Integer, primary_key=True)
    private_key = db.Column(db.Text, nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    key_size = db.Column(db.Integer, default=2048)  # in bits
    
    def __repr__(self):
        return f'<RSASecretContent id={self.id}>'

class AESSecretContent(db.Model):
    """Table to store AES-specific content"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text, nullable=False)
    key_size = db.Column(db.Integer, default=256)  # in bits
    iv = db.Column(db.Text, nullable=True)  # initialization vector
    
    def __repr__(self):
        return f'<AESSecretContent id={self.id}>'

class SecretTypeModel(db.Model):
    """Table to store secret types"""
    __tablename__ = 'secret_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<SecretType {self.name}>'

def initialize_secret_types():
    """Initialize secret types in the database"""
    for secret_type in SecretType:
        existing = SecretTypeModel.query.filter_by(name=secret_type.value).first()
        if not existing:
            new_type = SecretTypeModel(
                name=secret_type.value,
                description=f"Secret type for {secret_type.value} encryption"
            )
            db.session.add(new_type)
    
    db.session.commit()

class UserOperation(db.Model):
    """Table to store user operations"""
    __tablename__ = 'user_operations'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)  # Using created_by as user_id
    operation = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(UTC))
    details = db.Column(db.Text)
    
    def __repr__(self):
        return f'<UserOperation id={self.id} operation={self.operation}>'
