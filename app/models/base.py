from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from app.extensions import db

class BaseModel(db.Model):
    """Base model for all database models.
    
    Provides common fields and basic CRUD operations.
    """
    __abstract__ = True

    # Common fields
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    @declared_attr
    def __tablename__(cls):
        """Generate table name automatically from class name."""
        return cls.__name__.lower() + 's'

    def save(self):
        """Save the object to the database."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self, **kwargs):
        """Update object attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def delete(self):
        """Delete the object from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_by_id(cls, id):
        """Get a single object by ID."""
        return cls.query.get(id)

    @classmethod
    def get_all(cls, active_only=True):
        """Get all objects, optionally filtered by active status."""
        query = cls.query
        if active_only and hasattr(cls, "is_active"):
            query = query.filter_by(is_active=True)
        return query.all()

    @classmethod
    def get_first(cls, **filters):
        """Get the first object matching the filters."""
        return cls.query.filter_by(**filters).first()

    def to_dict(self):
        """Convert object to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        """String representation of the object."""
        return f'<{self.__class__.__name__} {self.id}>'
