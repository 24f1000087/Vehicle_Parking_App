"""
Parking spot model used for admin and user dashboards.
"""

from datetime import datetime

from extensions import db


class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(
        db.Integer, db.ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False
    )
    spot_number = db.Column(db.String(20), nullable=False, unique=True)
    status = db.Column(db.String(1), nullable=False, default="A", index=True)  # A/O
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parking_lot = db.relationship("ParkingLot", back_populates="spots")
    reservations = db.relationship(
        "Reservation", back_populates="parking_spot", cascade="all, delete-orphan"
    )

    def mark_available(self):
        self.status = "A"

    def mark_occupied(self):
        self.status = "O"

    def get_active_reservation(self):
        from models.reservation_model import Reservation
        return Reservation.query.filter_by(
            spot_id=self.id, status=Reservation.STATUS_ACTIVE
        ).first()

    def to_dict(self):
        label = self.spot_number
        data = {
            "id": self.id,
            "lot_id": self.lot_id,
            "spot_number": self.spot_number,
            "display_number": label,
            "status": self.status,
        }

        active_reservation = self.get_active_reservation() if self.status == "O" else None

        if active_reservation:
            data["current_reservation"] = active_reservation.to_dict(include_user=False)
            data["current_user"] = (
                active_reservation.user.to_dict() if active_reservation.user else None
            )

        return data

    def __repr__(self) -> str:
        return f"<ParkingSpot {self.spot_number} ({self.status})>"
