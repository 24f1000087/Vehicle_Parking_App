"""
Parking Lot Model
Represents parking lots in the system
"""

from extensions import db

class ParkingLot(db.Model):
    """Parking lot model"""
    
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price per hour
    number_of_spots = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert parking lot to dictionary"""
        available_spots = len([s for s in self.spots if s.status == 'A'])
        occupied_spots = len([s for s in self.spots if s.status == 'O'])
        
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'price': self.price,
            'number_of_spots': self.number_of_spots,
            'available_spots': available_spots,
            'occupied_spots': occupied_spots,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ParkingLot {self.name}>'

