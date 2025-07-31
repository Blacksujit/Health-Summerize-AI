"""
Configuration file for Hugging Face integration with Flask app.
Update these URLs based on your deployment environment.
"""

# Flask App URLs - Update these based on your deployment
FLASK_URLS = {
    "local": "http://127.0.0.1:600",
    "localhost": "http://localhost:600", 
    "production": "https://" if "" else "https://your-flask-app-domain.com",
    "direct_ip": "http://:600" if "" else "http://your-flask-app-ip:600"
}

# API Endpoints
API_ENDPOINTS = {
    "complete_appointment": "/complete_appointment",
    "validate_appointment": "/validate_appointment",
    "doctors_page": "/doctors"
}

# Timeout settings
TIMEOUT_SETTINGS = {
    "connection_timeout": 5,  # seconds
    "request_timeout": 10     # seconds
}

# Logging settings
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

def get_flask_urls():
    """Get list of Flask URLs to try."""
    return [
        f"{FLASK_URLS['local']}{API_ENDPOINTS['complete_appointment']}",
        f"{FLASK_URLS['localhost']}{API_ENDPOINTS['complete_appointment']}",
        f"{FLASK_URLS['production']}{API_ENDPOINTS['complete_appointment']}",
        f"{FLASK_URLS['direct_ip']}{API_ENDPOINTS['complete_appointment']}"
    ]

def get_doctors_page_urls():
    """Get list of doctors page URLs."""
    return {
        "local": f"{FLASK_URLS['local']}{API_ENDPOINTS['doctors_page']}",
        "production": f"{FLASK_URLS['production']}{API_ENDPOINTS['doctors_page']}"
    }
