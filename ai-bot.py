import http.client
import json

def call_ai_doctor_api(message, specialization="general", language="en"):
    """
    Calls the AI Doctor API and handles cached responses.
    """
    try:
        conn = http.client.HTTPSConnection("ai-doctor-api-ai-medical-chatbot-healthcare-ai-assistant.p.rapidapi.com")
        payload = json.dumps({
            "message": message,
            "specialization": specialization,
            "language": language
        })
        headers = {
            'x-rapidapi-key': "2408f98dfemshf58df2f19cfc556p1a26c5jsnac7fa5db12ad",
            'x-rapidapi-host': "ai-doctor-api-ai-medical-chatbot-healthcare-ai-assistant.p.rapidapi.com",
            'Content-Type': "application/json"
        }

        # Add nocache parameter to disable caching
        conn.request("POST", "/chat?noqueue=1&nocache=true", payload, headers)
        res = conn.getresponse()
        data = res.read()

        # Log the full response for debugging
        print("Full API Response:", data.decode("utf-8"))

        # Parse the API response
        response_data = json.loads(data.decode("utf-8"))

        # Handle the response
        if "message" in response_data:
            return response_data["message"]
        elif "cached" in response_data:
            return "Cached Response: " + str(response_data)
        else:
            return "Unexpected Response Format: " + str(response_data)
    except Exception as e:
        return f"Error: {str(e)}"

# Test the function
response = call_ai_doctor_api("What are the common symptoms of flu?", "general", "en")
print("AI Doctor Response:", response)