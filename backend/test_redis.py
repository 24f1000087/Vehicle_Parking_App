"""
Simple Redis Connection Test Script
Run this to verify Redis is working: python test_redis.py
"""

import redis

def test_redis_connection():
    """Test if Redis is accessible"""
    try:
        # Try to connect to Redis
        r = redis.from_url('redis://localhost:6379/0', decode_responses=True)
        
        # Test connection with a ping
        r.ping()
        print("✅ SUCCESS: Redis is running and accessible!")
        
        # Test set/get
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        if value == 'test_value':
            print("✅ SUCCESS: Redis read/write is working!")
        else:
            print("⚠️  WARNING: Redis read/write test failed")
        
        # Clean up
        r.delete('test_key')
        print("✅ Redis connection test completed successfully!")
        return True
        
    except redis.ConnectionError:
        print("❌ ERROR: Cannot connect to Redis!")
        print("\nTroubleshooting:")
        print("1. Make sure Docker Desktop is running")
        print("2. Start Redis with: docker run -d -p 6379:6379 --name redis-parking redis:latest")
        print("3. Check if Redis is running: docker ps")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    print("Testing Redis connection...")
    print("-" * 50)
    test_redis_connection()

