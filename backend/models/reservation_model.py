"""
Reservation model compatible with the frontend/API contract.
"""

from datetime import datetime

from extensions import db


class Reservation(db.Model):
    __tablename__ = "reservations"

    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    spot_id = db.Column(
        db.Integer, db.ForeignKey("parking_spots.id", ondelete="CASCADE"), nullable=False
    )
    lot_id = db.Column(
        db.Integer, db.ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False
    )
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_ACTIVE, index=True)
    vehicle_number = db.Column(db.String(20), nullable=True)
    cost = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", back_populates="reservations")
    parking_spot = db.relationship("ParkingSpot", back_populates="reservations")
    parking_lot = db.relationship("ParkingLot", back_populates="reservations")

    def calculate_cost(self, price_per_hour: float) -> float:
        """Compute and store the reservation cost."""
        end_time = self.end_time or datetime.utcnow()
        duration_hours = max((end_time - self.start_time).total_seconds() / 3600, 0)
        self.cost = round(duration_hours * price_per_hour, 2)
        return self.cost

    @property
    def duration_minutes(self) -> int:
        end_time = self.end_time or datetime.utcnow()
        return int(max((end_time - self.start_time).total_seconds() / 60, 0))

    def to_dict(self, include_user: bool = True):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "spot_id": self.spot_id,
            "lot_id": self.lot_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "cost": self.cost,
            "vehicle_number": self.vehicle_number,
            "duration_minutes": self.duration_minutes,
            "cost_so_far": round(
                (self.duration_minutes / 60)
                * (self.parking_lot.price if self.parking_lot else 0),
                2,
            ),
            "spot_number": self.parking_spot.spot_number if self.parking_spot else None,
            "lot_name": self.parking_lot.name if self.parking_lot else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_user and self.user:
            data["user"] = self.user.to_dict()

        return data

    def __repr__(self) -> str:
        return f"<Reservation {self.id} user={self.user_id} spot={self.spot_id}>"
