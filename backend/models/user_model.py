"""
User model backing authentication endpoints.

The frontend only collects a username and password, so we keep the schema lean
and avoid extra required fields such as email that would make registration
impossible.
"""

from datetime import datetime

from extensions import db
from werkzeug.security import check_password_hash, generate_password_hash


class User(db.Model):
    """Application user (either admin or standard user)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    pincode = db.Column(db.String(10), nullable=True)

    reservations = db.relationship(
        "Reservation", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """Store a hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Validate a password."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_private: bool = False):
        """Serialize the user for API responses."""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_private:
            data["pincode"] = self.pincode
        return data

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"

