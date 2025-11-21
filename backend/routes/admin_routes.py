"""
Admin Routes - FIXED
Handles admin-only operations: CRUD for parking lots, view users, charts, etc.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_
from models.user_model import User
from models.parkinglot_model import ParkingLot
from models.parkingspot_model import ParkingSpot
from models.reservation_model import Reservation
from utils.cache import cache_lot_status, get_cached_lot_status
from extensions import db
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Helper function to check if user is admin"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return False
    return True

@admin_bp.route('/parking-lots', methods=['GET'])
@jwt_required()
def get_all_parking_lots():
    """Get all parking lots (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        lots = ParkingLot.query.all()
        payload = [lot.to_dict() for lot in lots]
        return jsonify({
            'parking_lots': payload
        }), 200
    except Exception as e:
        print(f"Error in get_all_parking_lots: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots', methods=['POST'])
@jwt_required()
def create_parking_lot():
    """Create a new parking lot (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Get JSON data and handle empty/invalid requests
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['code', 'name', 'address', 'pincode', 'price', 'number_of_spots']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        lot_code = data['code'].strip().upper()
        lot_pincode = data['pincode'].strip()
        
        if not lot_code.isalnum():
            return jsonify({'error': 'Lot ID must be alphanumeric'}), 400
        
        if not lot_pincode.isdigit() or len(lot_pincode) != 6:
            return jsonify({'error': 'Pin code must be a 6-digit number'}), 400
        
        # Validate data types
        try:
            price = float(data['price'])
            number_of_spots = int(data['number_of_spots'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Price must be a number and number_of_spots must be an integer'}), 400
        
        if price < 0:
            return jsonify({'error': 'Price cannot be negative'}), 400
        
        if number_of_spots < 1:
            return jsonify({'error': 'Number of spots must be at least 1'}), 400
        
        # Check for duplicate codes/names to avoid database constraint errors
        existing = ParkingLot.query.filter(
            or_(ParkingLot.name == data['name'].strip(), ParkingLot.code == lot_code)
        ).first()
        if existing:
            return jsonify({'error': 'A parking lot with this name or ID already exists. Please choose a different value.'}), 400
        
        # Create parking lot
        new_lot = ParkingLot(
            code=lot_code,
            name=data['name'].strip(),
            address=data['address'].strip(),
            pincode=lot_pincode,
            price=price,
            number_of_spots=number_of_spots
        )
        
        db.session.add(new_lot)
        db.session.flush()  # Get the lot ID
        
        # Create parking spots
        for i in range(1, new_lot.number_of_spots + 1):
            row = chr(65 + (i - 1) // 10)
            col = ((i - 1) % 10) + 1
            public_label = f"{row}{col}"
            spot = ParkingSpot(
                lot_id=new_lot.id,
                spot_number=f"{new_lot.code}-{public_label}",
                status='A'
            )
            db.session.add(spot)
        
        db.session.commit()
        
        # Clear cache
        cache_lot_status(new_lot.id, new_lot.to_dict())
        
        return jsonify({
            'message': 'Parking lot created successfully',
            'parking_lot': new_lot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_parking_lot: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to create parking lot: {str(e)}'}), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['PUT'])
@jwt_required()
def update_parking_lot(lot_id):
    """Update a parking lot (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data and data['name']:
            lot.name = data['name'].strip()
        if 'address' in data and data['address']:
            lot.address = data['address'].strip()
        if 'pincode' in data and data['pincode']:
            pin = data['pincode'].strip()
            if not pin.isdigit() or len(pin) != 6:
                return jsonify({'error': 'Pin code must be a 6-digit number'}), 400
            lot.pincode = pin
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return jsonify({'error': 'Price cannot be negative'}), 400
                lot.price = price
            except (ValueError, TypeError):
                return jsonify({'error': 'Price must be a valid number'}), 400
        
        db.session.commit()
        
        # Update cache
        cache_lot_status(lot.id, lot.to_dict())
        
        return jsonify({
            'message': 'Parking lot updated successfully',
            'parking_lot': lot.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_parking_lot: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to update parking lot: {str(e)}'}), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['DELETE'])
@jwt_required()
def delete_parking_lot(lot_id):
    """Delete a parking lot (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        occupied_spots = ParkingSpot.query.filter_by(
            lot_id=lot_id, status='O'
        ).count()
        if occupied_spots > 0:
            return jsonify({'error': 'Cannot delete a lot while spots are occupied'}), 400

        db.session.delete(lot)
        db.session.commit()
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_parking_lot: {str(e)}")
        return jsonify({'error': f'Failed to delete parking lot: {str(e)}'}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        users = User.query.filter(User.role != 'admin').all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        print(f"Error in get_all_users: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/spots/<int:lot_id>', methods=['GET'])
@jwt_required()
def get_spots_by_lot(lot_id):
    """Get all spots for a specific lot (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        return jsonify({
            'spots': [spot.to_dict() for spot in spots]
        }), 200
    except Exception as e:
        print(f"Error in get_spots_by_lot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/spots/<int:spot_id>/details', methods=['GET'])
@jwt_required()
def get_spot_details(spot_id):
    """Get detailed information for a specific spot (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        spot = ParkingSpot.query.get(spot_id)
        if not spot:
            return jsonify({'error': 'Parking spot not found'}), 404

        lot = ParkingLot.query.get(spot.lot_id)
        active_reservation = Reservation.query.filter_by(
            spot_id=spot_id,
            status='active'
        ).first()

        response = {
            'spot': spot.to_dict(),
            'lot': {
                'id': lot.id,
                'name': lot.name,
                'price': lot.price
            } if lot else None,
            'reservation': active_reservation.to_dict() if active_reservation else None,
            'user': active_reservation.user.to_dict() if active_reservation and active_reservation.user else None
        }

        return jsonify(response), 200
    except Exception as e:
        print(f"Error in get_spot_details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>/spots/<int:spot_id>', methods=['DELETE'])
@jwt_required()
def delete_spot(lot_id, spot_id):
    """Delete a specific spot if it is not occupied"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot_id).first()
        if not spot:
            return jsonify({'error': 'Parking spot not found'}), 404

        if spot.status != 'A':
            return jsonify({'error': 'Cannot delete an occupied spot'}), 400

        active_reservation = Reservation.query.filter_by(
            spot_id=spot_id,
            status='active'
        ).first()

        if active_reservation:
            return jsonify({'error': 'Cannot delete a spot with an active reservation'}), 400

        lot = ParkingLot.query.get(lot_id)
        db.session.delete(spot)
        if lot and lot.number_of_spots > 0:
            lot.number_of_spots = max(0, lot.number_of_spots - 1)

        db.session.commit()
        if lot:
            cache_lot_status(lot.id, lot.to_dict())

        return jsonify({'message': 'Parking spot deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_spot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """Get summary statistics for admin dashboard (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        total_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        available_spots = ParkingSpot.query.filter_by(status='A').count()
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        total_users = User.query.filter_by(role='user').count()
        total_reservations = Reservation.query.count()
        active_reservations = Reservation.query.filter_by(status='active').count()
        
        # Revenue calculation (sum of all completed reservations)
        completed_reservations = Reservation.query.filter_by(status='completed').all()
        total_revenue = sum([r.cost for r in completed_reservations if r.cost]) or 0
        
        # Recent reservations (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_reservations = Reservation.query.filter(
            Reservation.created_at >= seven_days_ago
        ).count()
        
        return jsonify({
            'summary': {
                'total_lots': total_lots,
                'total_spots': total_spots,
                'available_spots': available_spots,
                'occupied_spots': occupied_spots,
                'total_users': total_users,
                'total_reservations': total_reservations,
                'active_reservations': active_reservations,
                'total_revenue': round(total_revenue, 2),
                'recent_reservations': recent_reservations
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/charts', methods=['GET'])
@jwt_required()
def get_chart_data():
    """Get chart data for admin dashboard (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Reservations per day (last 7 days)
        daily_reservations = []
        for i in range(6, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            count = Reservation.query.filter(
                Reservation.created_at >= start_of_day,
                Reservation.created_at <= end_of_day
            ).count()
            daily_reservations.append({
                'date': start_of_day.strftime('%Y-%m-%d'),
                'count': count
            })
        
        # Revenue per day (last 7 days)
        daily_revenue = []
        for i in range(6, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            reservations = Reservation.query.filter(
                Reservation.created_at >= start_of_day,
                Reservation.created_at <= end_of_day,
                Reservation.status == 'completed'
            ).all()
            revenue = sum([r.cost for r in reservations if r.cost]) or 0
            daily_revenue.append({
                'date': start_of_day.strftime('%Y-%m-%d'),
                'revenue': round(revenue, 2)
            })
        
        # Lot occupancy and revenue
        lots = ParkingLot.query.all()
        lot_occupancy = []
        lot_revenue = []
        for lot in lots:
            total = len(lot.spots)
            occupied = len([s for s in lot.spots if s.status == 'O'])
            lot_occupancy.append({
                'lot_name': lot.name,
                'occupied': occupied,
                'available': total - occupied
            })

            completed_reservations = Reservation.query.join(
                ParkingSpot, Reservation.spot_id == ParkingSpot.id
            ).filter(
                ParkingSpot.lot_id == lot.id,
                Reservation.status == 'completed'
            ).all()
            revenue = sum([r.cost for r in completed_reservations if r.cost]) or 0
            lot_revenue.append({
                'lot_name': lot.name,
                'revenue': round(revenue, 2)
            })
        
        return jsonify({
            'daily_reservations': daily_reservations,
            'daily_revenue': daily_revenue,
            'lot_occupancy': lot_occupancy,
            'lot_revenue': lot_revenue
        }), 200
        
    except Exception as e:
        print(f"Error in get_chart_data: {str(e)}")
        return jsonify({'error': str(e)}), 500