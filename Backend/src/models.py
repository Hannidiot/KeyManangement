from extensions import db

class RSAKeyPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    private_key = db.Column(db.Text, nullable=False)
    public_key = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<RSAKeyPair user_id={self.user_id}>'
    
