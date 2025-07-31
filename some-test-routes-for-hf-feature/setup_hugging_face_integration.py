#!/usr/bin/env python3
"""
Setup script for Hugging Face integration.
This script helps you configure the URLs for your deployment.
"""

import os
import sys
from pathlib import Path

def setup_configuration():
    """Interactive setup for Hugging Face integration configuration."""
    
    print("🔧 Hugging Face Integration Setup")
    print("=" * 50)
    print("This script will help you configure the URLs for your Flask app.")
    print()
    
    # Get current configuration
    config_file = Path("app/config.py")
    
    if config_file.exists():
        print("📁 Found existing configuration file")
        with open(config_file, 'r') as f:
            current_config = f.read()
        
        # Extract current URLs
        if "your-flask-app-domain.com" in current_config:
            print("⚠️  Configuration needs to be updated with your actual URLs")
        else:
            print("✅ Configuration appears to be set up")
    else:
        print("📁 No configuration file found")
    
    print("\n" + "=" * 50)
    print("🌐 URL Configuration")
    print("=" * 50)
    
    # Get user input
    print("\n1. Local Development URLs:")
    local_port = input("   Flask app port (default: 600): ").strip() or "600"
    
    print("\n2. Production URLs:")
    production_domain = input("   Production domain (e.g., myapp.com): ").strip()
    production_ip = input("   Production IP address (optional): ").strip()
    
    # Create configuration
    config_content = f'''"""
Configuration file for Hugging Face integration with Flask app.
Update these URLs based on your deployment environment.
"""

# Flask App URLs - Update these based on your deployment
FLASK_URLS = {{
    "local": "http://127.0.0.1:{local_port}",
    "localhost": "http://localhost:{local_port}", 
    "production": "https://{production_domain}" if "{production_domain}" else "https://your-flask-app-domain.com",
    "direct_ip": "http://{production_ip}:{local_port}" if "{production_ip}" else "http://your-flask-app-ip:{local_port}"
}}

# API Endpoints
API_ENDPOINTS = {{
    "complete_appointment": "/complete_appointment",
    "validate_appointment": "/validate_appointment",
    "doctors_page": "/doctors"
}}

# Timeout settings
TIMEOUT_SETTINGS = {{
    "connection_timeout": 5,  # seconds
    "request_timeout": 10     # seconds
}}

# Logging settings
LOGGING_CONFIG = {{
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}}

def get_flask_urls():
    """Get list of Flask URLs to try."""
    return [
        f"{{FLASK_URLS['local']}}{{API_ENDPOINTS['complete_appointment']}}",
        f"{{FLASK_URLS['localhost']}}{{API_ENDPOINTS['complete_appointment']}}",
        f"{{FLASK_URLS['production']}}{{API_ENDPOINTS['complete_appointment']}}",
        f"{{FLASK_URLS['direct_ip']}}{{API_ENDPOINTS['complete_appointment']}}"
    ]

def get_doctors_page_urls():
    """Get list of doctors page URLs."""
    return {{
        "local": f"{{FLASK_URLS['local']}}{{API_ENDPOINTS['doctors_page']}}",
        "production": f"{{FLASK_URLS['production']}}{{API_ENDPOINTS['doctors_page']}}"
    }}
'''
    
    # Write configuration
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"\n✅ Configuration saved to {config_file}")
        
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return False
    
    # Show summary
    print("\n" + "=" * 50)
    print("📋 Configuration Summary")
    print("=" * 50)
    print(f"Local URLs: http://127.0.0.1:{local_port}")
    print(f"Production Domain: {production_domain or 'Not set'}")
    print(f"Production IP: {production_ip or 'Not set'}")
    
    return True

def test_flask_connection():
    """Test connection to Flask app."""
    
    print("\n" + "=" * 50)
    print("🧪 Testing Flask Connection")
    print("=" * 50)
    
    try:
        import requests
        from app.config import get_flask_urls
        
        flask_urls = get_flask_urls()
        
        for url in flask_urls:
            try:
                print(f"Testing: {url}")
                response = requests.get(url.replace('/complete_appointment', '/'), timeout=5)
                if response.status_code == 200:
                    print(f"✅ Success: {url}")
                    return True
                else:
                    print(f"⚠️  Response {response.status_code}: {url}")
            except requests.exceptions.ConnectionError:
                print(f"❌ Connection failed: {url}")
            except Exception as e:
                print(f"❌ Error: {url} - {e}")
        
        print("\n❌ No Flask app connections successful")
        return False
        
    except ImportError:
        print("❌ Requests library not available")
        return False

def show_next_steps():
    """Show next steps for deployment."""
    
    print("\n" + "=" * 50)
    print("🚀 Next Steps")
    print("=" * 50)
    
    print("1. Start your Flask app:")
    print("   python app.py")
    
    print("\n2. Test the connection:")
    print("   python setup_hugging_face_integration.py --test")
    
    print("\n3. Deploy to Hugging Face:")
    print("   - Copy app/hugging_face_script.py to your Hugging Face space")
    print("   - Copy app/config.py to your Hugging Face space")
    print("   - Deploy the space")
    
    print("\n4. Test the complete flow:")
    print("   - Book an appointment in Flask app")
    print("   - Validate appointment to redirect to Hugging Face")
    print("   - Use AI analysis tools")
    print("   - Click 'End Consultation'")
    print("   - Verify return to doctors page")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode
        test_flask_connection()
    else:
        # Setup mode
        if setup_configuration():
            show_next_steps()
            
            # Ask if user wants to test
            test_now = input("\nWould you like to test the connection now? (y/n): ").strip().lower()
            if test_now == 'y':
                test_flask_connection()
        else:
            print("\n❌ Setup failed. Please check the errors above.") 