from datetime import datetime
from app.extensions import db

class BaseModel(db.Model):
    """Base model that includes common columns and methods"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def save(self):
        """Save the current model to the database"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Delete the current model from the database"""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """Get a model by its ID"""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Get all instances of the model"""
        return cls.query.all()
