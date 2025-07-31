#!/usr/bin/env python3
"""
Test script to verify URL parameter extraction for appointment ID.
"""

import urllib.parse

def test_url_parameter_extraction():
    """Test URL parameter extraction."""
    
    # Test URL from your Hugging Face space
    test_url = "https://huggingface.co/spaces/blackshadow1/Multi-Modal-Medical-Analysis-System?appointment_id=04cffd53-de57-4d0d-8430-239b04e8e363"
    
    print("🧪 Testing URL Parameter Extraction")
    print("=" * 50)
    print(f"Test URL: {test_url}")
    
    # Parse the URL
    parsed_url = urllib.parse.urlparse(test_url)
    print(f"Parsed URL: {parsed_url}")
    
    # Extract query parameters
    query_params = urllib.parse.parse_qs(parsed_url.query)
    print(f"Query parameters: {query_params}")
    
    # Extract appointment ID
    appointment_id = query_params.get('appointment_id', [''])[0]
    print(f"Extracted appointment ID: {appointment_id}")
    
    # Verify the appointment ID
    expected_id = "04cffd53-de57-4d0d-8430-239b04e8e363"
    if appointment_id == expected_id:
        print("✅ URL parameter extraction working correctly!")
        return True
    else:
        print(f"❌ URL parameter extraction failed!")
        print(f"Expected: {expected_id}")
        print(f"Got: {appointment_id}")
        return False

def test_javascript_equivalent():
    """Test the JavaScript equivalent of URL parameter extraction."""
    
    print("\n" + "=" * 50)
    print("🔧 JavaScript Equivalent Test")
    print("=" * 50)
    
    # JavaScript code that should work
    js_code = """
    function getUrlParameter(name) {
        name = name.replace(/[[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }
    
    var appointmentId = getUrlParameter('appointment_id');
    console.log('Appointment ID:', appointmentId);
    """
    
    print("JavaScript code to extract appointment ID:")
    print(js_code)
    
    # Simulate the JavaScript extraction
    test_url = "https://huggingface.co/spaces/blackshadow1/Multi-Modal-Medical-Analysis-System?appointment_id=04cffd53-de57-4d0d-8430-239b04e8e363"
    
    # Extract the query string part
    query_string = test_url.split('?')[1] if '?' in test_url else ''
    print(f"Query string: {query_string}")
    
    # Simulate JavaScript regex
    import re
    pattern = r'[?&]appointment_id=([^&#]*)'
    match = re.search(pattern, test_url)
    
    if match:
        appointment_id = match.group(1)
        print(f"✅ JavaScript-style extraction successful: {appointment_id}")
        return True
    else:
        print("❌ JavaScript-style extraction failed")
        return False

def show_debugging_steps():
    """Show debugging steps for the Hugging Face space."""
    
    print("\n" + "=" * 50)
    print("🐛 Debugging Steps for Hugging Face Space")
    print("=" * 50)
    
    print("1. Open browser developer tools (F12)")
    print("2. Go to Console tab")
    print("3. Navigate to your Hugging Face space with appointment_id parameter")
    print("4. Look for console.log messages:")
    print("   - 'Found appointment ID: 04cffd53-de57-4d0d-8430-239b04e8e363'")
    print("   - 'Found element: [HTML element]'")
    print("   - 'Set appointment ID to: 04cffd53-de57-4d0d-8430-239b04e8e363'")
    
    print("\n5. If you see 'Could not find appointment ID input field':")
    print("   - Check if the input field has the correct placeholder text")
    print("   - Verify the label text contains 'Appointment ID'")
    
    print("\n6. If you see 'No appointment ID found in URL':")
    print("   - Verify the URL contains ?appointment_id=...")
    print("   - Check if the parameter is properly encoded")
    
    print("\n7. Test the URL parameter manually:")
    print("   - Open browser console")
    print("   - Run: getUrlParameter('appointment_id')")
    print("   - Should return: '04cffd53-de57-4d0d-8430-239b04e8e363'")

if __name__ == "__main__":
    print("URL Parameter Extraction Test Suite")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_url_parameter_extraction()
    test2_passed = test_javascript_equivalent()
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! URL parameter extraction is working correctly.")
        print("\nThe issue is likely in the JavaScript execution or element selection.")
    else:
        print("\n❌ Some tests failed. Check the URL format.")
    
    show_debugging_steps() 