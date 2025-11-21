"""
User Routes
Handles user operations: book spot, vacate spot, view reservations, export CSV
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_model import User
from models.parkinglot_model import ParkingLot
from models.parkingspot_model import ParkingSpot
from models.reservation_model import Reservation
from utils.cache import cache_lot_status, get_cached_lot_status
# Note: utils.tasks import moved to function level to avoid circular import
from extensions import db
from datetime import datetime, timedelta
import csv
import io
import re
from pytz import timezone, utc

user_bp = Blueprint('user', __name__)

@user_bp.route('/parking-lots', methods=['GET'])
@jwt_required()
def get_available_parking_lots():
    """Get all parking lots with availability (user view)"""
    try:
        lots = ParkingLot.query.all()
        result = []
        
        for lot in lots:
            # Try to get from cache first
            cached = get_cached_lot_status(lot.id)
            if cached:
                result.append(cached)
            else:
                lot_dict = lot.to_dict()
                cache_lot_status(lot.id, lot_dict)
                result.append(lot_dict)
        
        return jsonify({
            'parking_lots': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/book', methods=['POST'])
@jwt_required()
def book_spot():
    """Book an available parking spot (auto-allocates first available)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or not data.get('lot_id') or not data.get('vehicle_number'):
            return jsonify({'error': 'lot_id and vehicle_number are required'}), 400
        
        lot_id = int(data['lot_id'])
        vehicle_number = data.get('vehicle_number', '').upper().replace(" ", "")
        
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$', vehicle_number):
            return jsonify({'error': 'Invalid vehicle number. Use format like KA01AB1234'}), 400
        lot = ParkingLot.query.get(lot_id)
        
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        # Check if user has an active reservation
        active_reservation = Reservation.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if active_reservation:
            return jsonify({'error': 'You already have an active reservation'}), 400
        
        # Find first available spot in the lot
        available_spot = ParkingSpot.query.filter_by(
            lot_id=lot_id,
            status='A'
        ).first()
        
        if not available_spot:
            return jsonify({'error': 'No available spots in this parking lot'}), 400
        
        # Create reservation
        reservation = Reservation(
            spot_id=available_spot.id,
            lot_id=lot_id,
            user_id=user_id,
            start_time=datetime.utcnow(),
            status='active',
            vehicle_number=vehicle_number
        )
        
        # Update spot status
        available_spot.status = 'O'
        
        db.session.add(reservation)
        db.session.commit()
        
        # Update cache
        db.session.refresh(lot)
        cache_lot_status(lot_id, lot.to_dict())
        
        return jsonify({
            'message': 'Spot booked successfully',
            'reservation': reservation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/vacate', methods=['POST'])
@jwt_required()
def vacate_spot():
    """Vacate current parking spot and calculate cost"""
    try:
        user_id = int(get_jwt_identity())
        
        # Find active reservation
        reservation = Reservation.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not reservation:
            return jsonify({'error': 'No active reservation found'}), 404
        
        # Get parking lot to get price
        spot = ParkingSpot.query.get(reservation.spot_id)
        if not spot:
            return jsonify({'error': 'Parking spot not found'}), 404
        
        lot = ParkingLot.query.get(spot.lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        # Calculate cost
        reservation.end_time = datetime.utcnow()
        reservation.calculate_cost(lot.price)
        reservation.status = 'completed'
        
        # Update spot status
        spot.status = 'A'
        
        db.session.commit()
        
        # Update cache
        db.session.refresh(lot)
        cache_lot_status(lot.id, lot.to_dict())
        
        return jsonify({
            'message': 'Spot vacated successfully',
            'reservation': reservation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reservations', methods=['GET'])
@jwt_required()
def get_my_reservations():
    """Get all reservations for current user"""
    try:
        user_id = int(get_jwt_identity())
        
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(
            Reservation.created_at.desc()
        ).all()
        
        return jsonify({
            'reservations': [r.to_dict() for r in reservations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reservations/active', methods=['GET'])
@jwt_required()
def get_active_reservation():
    """Get active reservation for current user"""
    try:
        user_id = int(get_jwt_identity())
        
        reservation = Reservation.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not reservation:
            return jsonify({'reservation': None}), 200
        
        return jsonify({
            'reservation': reservation.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/export-csv', methods=['GET'])
@jwt_required()
def export_csv():
    """Export user's reservations as CSV (triggers async task)"""
    try:
        # Lazy import to avoid circular dependency
        from utils.tasks import export_reservations_csv
        
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Trigger async CSV export task
        task = export_reservations_csv.delay(user_id)
        
        return jsonify({
            'message': 'CSV export started',
            'task_id': task.id
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/export-csv-sync', methods=['GET'])
@jwt_required()
def export_csv_sync():
    """Export user's reservations as CSV synchronously (immediate download)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all reservations
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(
            Reservation.created_at.desc()
        ).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Reservation ID',
            'Spot Number',
            'Lot Name',
            'Start Time',
            'End Time',
            'Cost',
            'Status',
            'Created At'
        ])
        
        ist = timezone('Asia/Kolkata')

        def to_ist(dt):
            if not dt:
                return None
            if dt.tzinfo is None:
                dt = utc.localize(dt)
            return dt.astimezone(ist)

        # Write data
        for res in reservations:
            start = to_ist(res.start_time)
            end = to_ist(res.end_time)
            created = to_ist(res.created_at)
            writer.writerow([
                res.id,
                res.parking_spot.spot_number if res.parking_spot else 'N/A',
                res.parking_spot.parking_lot.name if res.parking_spot and res.parking_spot.parking_lot else 'N/A',
                start.strftime('%d-%m-%Y %H:%M:%S') if start else 'N/A',
                end.strftime('%d-%m-%Y %H:%M:%S') if end else 'N/A',
                res.cost or 'N/A',
                res.status,
                created.strftime('%d-%m-%Y %H:%M:%S') if created else 'N/A'
            ])
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=reservations_{user.username}_{datetime.now().strftime("%Y%m%d")}.csv'
            }
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_user_summary():
    """Get summary metrics for the current user"""
    try:
        user_id = int(get_jwt_identity())

        total_reservations = Reservation.query.filter_by(user_id=user_id).count()
        completed_reservations = Reservation.query.filter_by(
            user_id=user_id,
            status='completed'
        ).all()
        active_reservation = Reservation.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

        total_spent = sum([res.cost or 0 for res in completed_reservations])
        total_hours = 0
        for res in completed_reservations:
            if res.start_time:
                end_time = res.end_time or datetime.utcnow()
                total_hours += max((end_time - res.start_time).total_seconds() / 3600, 0)

        summary = {
            'total_reservations': total_reservations,
            'completed_reservations': len(completed_reservations),
            'active_reservation': active_reservation.to_dict() if active_reservation else None,
            'total_spent': round(total_spent, 2),
            'total_hours': round(total_hours, 2)
        }

        return jsonify({'summary': summary}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/charts', methods=['GET'])
@jwt_required()
def get_user_chart_data():
    """Get chart data for the current user"""
    try:
        user_id = int(get_jwt_identity())

        # Daily usage for last 7 days
        daily_usage = []
        for i in range(6, -1, -1):
            day = datetime.utcnow() - timedelta(days=i)
            start_of_day = day.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            count = Reservation.query.filter(
                Reservation.user_id == user_id,
                Reservation.created_at >= start_of_day,
                Reservation.created_at <= end_of_day
            ).count()
            daily_usage.append({
                'date': start_of_day.strftime('%Y-%m-%d'),
                'count': count
            })

        # Lot distribution
        lot_distribution_map = {}
        user_reservations = Reservation.query.filter_by(user_id=user_id).all()
        for res in user_reservations:
            lot_name = 'Unknown'
            if res.parking_spot and res.parking_spot.parking_lot:
                lot_name = res.parking_spot.parking_lot.name
            lot_distribution_map[lot_name] = lot_distribution_map.get(lot_name, 0) + 1

        lot_distribution = [
            {'lot': lot, 'count': count}
            for lot, count in lot_distribution_map.items()
        ]

        status_breakdown = [
            {'label': 'Active', 'count': Reservation.query.filter_by(user_id=user_id, status='active').count()},
            {'label': 'Completed', 'count': Reservation.query.filter_by(user_id=user_id, status='completed').count()}
        ]

        return jsonify({
            'daily_usage': daily_usage,
            'lot_distribution': lot_distribution,
            'status_breakdown': status_breakdown
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

