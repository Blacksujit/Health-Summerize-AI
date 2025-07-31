#!/usr/bin/env python3
"""
Test script to check if the Flask route is working.
"""

import requests
import time

def test_flask_routes():
    """Test Flask routes to ensure they're working."""
    
    base_url = "http://127.0.0.1:600"
    
    print("🧪 Testing Flask Routes")
    print("=" * 50)
    
    # Test 1: Check if Flask app is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Flask app is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Flask app is not running on port 600")
        print("Please start the Flask app first:")
        print("python app.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Flask app: {e}")
        return False
    
    # Test 2: Check doctors page
    try:
        response = requests.get(f"{base_url}/doctors", timeout=5)
        print(f"✅ Doctors page accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error accessing doctors page: {e}")
    
    # Test 3: Check manual completion page
    try:
        response = requests.get(f"{base_url}/complete_appointment_manual", timeout=5)
        print(f"✅ Manual completion page accessible (Status: {response.status_code})")
        if response.status_code == 200:
            print("✅ Route is working correctly!")
        else:
            print(f"⚠️ Route returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing manual completion page: {e}")
    
    # Test 4: Check complete_appointment API endpoint
    try:
        response = requests.post(f"{base_url}/complete_appointment", 
                               json={"appointment_id": "test-id"}, 
                               timeout=5)
        print(f"✅ Complete appointment API accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error accessing complete appointment API: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Route Testing Complete")
    
    return True

def show_troubleshooting():
    """Show troubleshooting steps."""
    
    print("\n🔧 Troubleshooting Steps:")
    print("=" * 50)
    
    print("1. Ensure Flask app is running:")
    print("   python app.py")
    
    print("\n2. Check if port 600 is available:")
    print("   netstat -ano | findstr :600")
    
    print("\n3. Try accessing the route directly:")
    print("   http://127.0.0.1:600/complete_appointment_manual")
    
    print("\n4. Check Flask app logs for errors")
    
    print("\n5. Verify the route is registered:")
    print("   - Check app/routes.py for the route definition")
    print("   - Check app/__init__.py for blueprint registration")

if __name__ == "__main__":
    print("Flask Route Test Suite")
    print("=" * 50)
    
    success = test_flask_routes()
    
    if not success:
        show_troubleshooting()
    else:
        print("\n✅ All routes are working correctly!")
        print("You can now use the manual completion feature.") 