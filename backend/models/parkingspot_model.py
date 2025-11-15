"""
Parking Spot Model
Represents individual parking spots within a lot
"""

from extensions import db

class ParkingSpot(db.Model):
    """Parking spot model"""
    
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # 'A' = Available, 'O' = Occupied
    spot_number = db.Column(db.String(20), nullable=False)  # e.g., "A1", "B2"
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert parking spot to dictionary"""
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'status': self.status,
            'spot_number': self.spot_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} - {self.status}>'

