"""
API Testing Script
Run this to test all API endpoints and diagnose issues
Usage: python test_api.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Health check passed: {response.json()}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend! Make sure Flask is running on port 5000")
        return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_login():
    """Test login endpoint"""
    print("\n" + "="*60)
    print("Testing Login Endpoint")
    print("="*60)
    
    # Test admin login
    try:
        print_info("Attempting admin login...")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print_success(f"Admin login successful! Token: {token[:20]}...")
            return token
        else:
            print_error(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None

def test_admin_endpoints(token):
    """Test admin endpoints"""
    print("\n" + "="*60)
    print("Testing Admin Endpoints")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test summary
    try:
        print_info("Testing GET /api/admin/summary...")
        response = requests.get(f"{BASE_URL}/admin/summary", headers=headers, timeout=5)
        if response.status_code == 200:
            print_success(f"Summary endpoint works: {response.json()}")
        else:
            print_error(f"Summary failed: {response.status_code} - {response.text}")
    except Exception as e:
        print_error(f"Summary error: {str(e)}")
    
    # Test get parking lots
    try:
        print_info("Testing GET /api/admin/parking-lots...")
        response = requests.get(f"{BASE_URL}/admin/parking-lots", headers=headers, timeout=5)
        if response.status_code == 200:
            lots = response.json().get('parking_lots', [])
            print_success(f"Parking lots endpoint works: {len(lots)} lots found")
        else:
            print_error(f"Parking lots failed: {response.status_code} - {response.text}")
    except Exception as e:
        print_error(f"Parking lots error: {str(e)}")
    
    # Test create parking lot
    try:
        print_info("Testing POST /api/admin/parking-lots...")
        test_lot = {
            "name": f"Test Lot {datetime.now().strftime('%H%M%S')}",
            "address": "123 Test Street",
            "price": 10.5,
            "number_of_spots": 5
        }
        
        print_info(f"Sending data: {json.dumps(test_lot, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/admin/parking-lots",
            json=test_lot,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 201:
            print_success(f"Create parking lot works: {response.json()}")
            return response.json().get('parking_lot', {}).get('id')
        else:
            print_error(f"Create parking lot failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Create parking lot error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_user_endpoints(token):
    """Test user endpoints"""
    print("\n" + "="*60)
    print("Testing User Endpoints")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test get parking lots
    try:
        print_info("Testing GET /api/user/parking-lots...")
        response = requests.get(f"{BASE_URL}/user/parking-lots", headers=headers, timeout=5)
        if response.status_code == 200:
            lots = response.json().get('parking_lots', [])
            print_success(f"User parking lots endpoint works: {len(lots)} lots available")
        else:
            print_error(f"User parking lots failed: {response.status_code} - {response.text}")
    except Exception as e:
        print_error(f"User parking lots error: {str(e)}")
    
    # Test get reservations
    try:
        print_info("Testing GET /api/user/reservations...")
        response = requests.get(f"{BASE_URL}/user/reservations", headers=headers, timeout=5)
        if response.status_code == 200:
            reservations = response.json().get('reservations', [])
            print_success(f"Reservations endpoint works: {len(reservations)} reservations found")
        else:
            print_error(f"Reservations failed: {response.status_code} - {response.text}")
    except Exception as e:
        print_error(f"Reservations error: {str(e)}")

def test_cors():
    """Test CORS headers"""
    print("\n" + "="*60)
    print("Testing CORS Configuration")
    print("="*60)
    
    try:
        print_info("Testing CORS preflight...")
        response = requests.options(
            f"{BASE_URL}/admin/parking-lots",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print_success("CORS preflight successful")
            cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
            for header, value in cors_headers.items():
                print_info(f"  {header}: {value}")
        else:
            print_warning(f"CORS preflight returned: {response.status_code}")
    except Exception as e:
        print_error(f"CORS test error: {str(e)}")

def main():
    """Run all tests"""
    print("\n" + "🚗 " * 20)
    print("Vehicle Parking App - API Test Suite")
    print("🚗 " * 20)
    
    # Test 1: Health check
    if not test_health():
        print_error("\n⛔ Backend is not running! Please start Flask first.")
        print_info("Run: cd backend && flask run")
        return
    
    # Test 2: CORS
    test_cors()
    
    # Test 3: Login
    token = test_login()
    if not token:
        print_error("\n⛔ Login failed! Cannot proceed with authenticated tests.")
        return
    
    # Test 4: Admin endpoints
    lot_id = test_admin_endpoints(token)
    
    # Test 5: User endpoints
    test_user_endpoints(token)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print_info("All basic tests completed. Check output above for any errors.")
    print_info("\nIf you see 422 errors:")
    print_info("  - Make sure Content-Type: application/json header is set")
    print_info("  - Verify JSON data is properly formatted")
    print_info("  - Check that all required fields are included")
    
    print_info("\nIf you see CORS errors:")
    print_info("  - Restart Flask backend")
    print_info("  - Make sure frontend is on http://localhost:8080")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()