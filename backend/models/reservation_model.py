"""
Reservation Model
Represents parking reservations made by users
"""

from extensions import db
from datetime import datetime

class Reservation(db.Model):
    """Reservation model"""
    
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)  # Null if still active
    cost = db.Column(db.Float, nullable=True)  # Calculated when reservation ends
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active' or 'completed'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def calculate_cost(self, price_per_hour):
        """Calculate cost based on hours and price per hour"""
        if self.end_time and self.start_time:
            duration = (self.end_time - self.start_time).total_seconds() / 3600  # Convert to hours
            self.cost = round(duration * price_per_hour, 2)
        return self.cost
    
    def to_dict(self):
        """Convert reservation to dictionary"""
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'cost': self.cost,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'spot_number': self.parking_spot.spot_number if self.parking_spot else None,
            'lot_name': self.parking_spot.parking_lot.name if self.parking_spot and self.parking_spot.parking_lot else None
        }
    
    def __repr__(self):
        return f'<Reservation {self.id} - User {self.user_id}>'

