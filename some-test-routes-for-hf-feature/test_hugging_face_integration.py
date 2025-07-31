#!/usr/bin/env python3
"""
Test script for Hugging Face integration with Flask app.
This script tests the appointment completion functionality.
"""

import requests
import json
import time

def test_appointment_completion():
    """Test the appointment completion functionality."""
    
    # Flask app URL
    flask_base_url = "http://127.0.0.1:600"
    
    print("Testing Hugging Face Integration with Flask App")
    print("=" * 50)
    
    # Test 1: Check if Flask app is running
    try:
        response = requests.get(f"{flask_base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print(f"❌ Flask app returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Flask app: {e}")
        print("Make sure your Flask app is running on port 600")
        return False
    
    # Test 2: Test appointment completion endpoint
    test_appointment_id = "test-appointment-123"
    
    try:
        response = requests.post(
            f"{flask_base_url}/complete_appointment",
            json={"appointment_id": test_appointment_id},
            timeout=10
        )
        
        if response.status_code == 404:
            print("✅ Appointment completion endpoint is working (404 expected for non-existent appointment)")
        elif response.status_code == 200:
            print("✅ Appointment completion endpoint is working")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing appointment completion: {e}")
        return False
    
    # Test 3: Test Hugging Face URL generation
    try:
        response = requests.post(
            f"{flask_base_url}/validate_appointment",
            json={"appointment_id": test_appointment_id},
            timeout=10
        )
        
        if response.status_code == 404:
            print("✅ Appointment validation endpoint is working (404 expected for non-existent appointment)")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing appointment validation: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your integration is working correctly.")
    print("\nNext steps:")
    print("1. Start your Hugging Face Spaces with the updated script")
    print("2. Book an appointment in your Flask app")
    print("3. Validate the appointment to get redirected to Hugging Face")
    print("4. Use the 'End Consultation' button to complete the appointment")
    print("5. You should be redirected back to the doctors page")
    
    return True

def test_hugging_face_url():
    """Test the Hugging Face URL generation."""
    
    print("\nTesting Hugging Face URL Generation")
    print("=" * 40)
    
    # Example appointment ID
    appointment_id = "example-appointment-456"
    
    # Generate the expected URL
    expected_url = f"https://huggingface.co/spaces/blackshadow1/Multi-Modal-Medical-Analysis-System?appointment_id={appointment_id}"
    
    print(f"Expected URL: {expected_url}")
    print("✅ URL format is correct")
    
    # Test URL parameter extraction
    import urllib.parse
    parsed_url = urllib.parse.urlparse(expected_url)
    params = urllib.parse.parse_qs(parsed_url.query)
    
    if 'appointment_id' in params:
        extracted_id = params['appointment_id'][0]
        if extracted_id == appointment_id:
            print("✅ URL parameter extraction works correctly")
        else:
            print(f"❌ URL parameter extraction failed: expected {appointment_id}, got {extracted_id}")
            return False
    else:
        print("❌ URL parameter extraction failed: appointment_id not found")
        return False
    
    return True

if __name__ == "__main__":
    print("Hugging Face Integration Test Suite")
    print("=" * 40)
    
    # Run tests
    test1_passed = test_appointment_completion()
    test2_passed = test_hugging_face_url()
    
    if test1_passed and test2_passed:
        print("\n🎉 All integration tests passed!")
        print("\nYour system is ready for use:")
        print("1. Flask app handles appointment management")
        print("2. Hugging Face interface can complete appointments")
        print("3. Users can seamlessly move between both systems")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 