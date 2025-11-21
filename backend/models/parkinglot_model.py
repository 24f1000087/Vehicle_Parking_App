"""
Parking lot model aligned with the REST routes used by the Vue dashboard.
"""

from datetime import datetime

from extensions import db


class ParkingLot(db.Model):
    __tablename__ = "parking_lots"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    pincode = db.Column(db.String(10), nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    number_of_spots = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    spots = db.relationship(
        "ParkingSpot",
        back_populates="parking_lot",
        cascade="all, delete-orphan",
        order_by="ParkingSpot.spot_number",
    )
    reservations = db.relationship(
        "Reservation", back_populates="parking_lot", cascade="all, delete-orphan"
    )

    @property
    def available_spots(self) -> int:
        return sum(1 for spot in self.spots if spot.status == "A")

    @property
    def occupied_spots(self) -> int:
        return self.number_of_spots - self.available_spots

    def to_dict(self, include_spots: bool = True):
        data = {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "address": self.address,
            "pincode": self.pincode,
            "price": self.price,
            "number_of_spots": self.number_of_spots,
            "available_spots": self.available_spots,
            "occupied_spots": self.occupied_spots,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_spots:
            spots = [spot.to_dict() for spot in self.spots]
            data["spots"] = spots
            data["occupants"] = [
                {
                    "spot_id": spot["id"],
                    "spot_number": spot["spot_number"],
                    "user": spot.get("current_user"),
                    "reservation": spot.get("current_reservation"),
                }
                for spot in spots
                if spot["status"] == "O" and spot.get("current_user")
            ]
        return data

    def __repr__(self) -> str:
        return f"<ParkingLot {self.name}>"
