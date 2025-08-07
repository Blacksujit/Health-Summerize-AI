# 🚨 Quick Fix Guide - Connection Error

## ❌ Problem
```
Error Completing Consultation
Error: HTTPConnectionPool(host='127.0.0.1', port=600): Max retries exceeded with url: /complete_appointment (Caused by NewConnectionError(': Failed to establish a new connection: [Errno 111] Connection refused'))
```

## 🔧 Immediate Solutions

### Solution 1: Start Your Flask App (Most Common Fix)

1. **Open a new terminal/command prompt**
2. **Navigate to your project directory**:
   ```bash
   cd AI-Health-Summerize
   ```
3. **Start the Flask app**:
   ```bash
   python app.py
   ```
4. **Verify it's running**: You should see output like:
   ```
   * Running on http://127.0.0.1:600
   * Debug mode: on
   ```

### Solution 2: Check if Port 600 is Available

**Windows:**
```bash
netstat -an | findstr :600
```

**Linux/Mac:**
```bash
netstat -an | grep :600
```

If port 600 is in use, either:
- Kill the process using port 600
- Or change the port in `app.py`

### Solution 3: Use Different Port

If port 600 is busy, edit `app.py` and change:
```python
socketio.run(app, debug=True, port=600)
```
to:
```python
socketio.run(app, debug=True, port=5000)
```

Then update `app/config.py`:
```python
FLASK_URLS = {
    "local": "http://127.0.0.1:5000",  # Changed from 600
    "localhost": "http://localhost:5000",  # Changed from 600
    # ... rest of config
}
```

## 🧪 Test the Fix

### Step 1: Run Setup Script
```bash
python setup_hugging_face_integration.py
```

### Step 2: Test Connection
```bash
python setup_hugging_face_integration.py --test
```

### Step 3: Test Complete Flow
```bash
python test_hugging_face_integration.py
```

## 🚀 For Production Deployment

### If You're Deploying to Hugging Face Spaces

The issue is that Hugging Face Spaces run in the cloud and can't access your local Flask server. You need to:

1. **Deploy your Flask app to a public server** (Heroku, AWS, etc.)
2. **Update the configuration** with your public URL
3. **Deploy the updated Hugging Face script**

### Quick Production Setup

1. **Update `app/config.py`** with your production URL:
   ```python
   FLASK_URLS = {
       "local": "http://127.0.0.1:600",
       "localhost": "http://localhost:600", 
       "production": "https://your-actual-domain.com",  # Update this
       "direct_ip": "http://your-server-ip:600"  # Update this
   }
   ```

2. **Deploy Flask app** to a public server

3. **Deploy Hugging Face script** with updated config

## 🔍 Troubleshooting Checklist

- [ ] Flask app is running (`python app.py`)
- [ ] Flask app is accessible at `http://127.0.0.1:600`
- [ ] Port 600 is not blocked by firewall
- [ ] No other process is using port 600
- [ ] Network connectivity is working
- [ ] Configuration file is properly set up

## 📞 If Still Not Working

1. **Check Flask app logs** for errors
2. **Try a different port** (5000, 8000, etc.)
3. **Test with curl**:
   ```bash
   curl http://127.0.0.1:600/
   ```
4. **Check if Flask app starts without errors**

## 🎯 Expected Result

After fixing, when you click "End Consultation" in Hugging Face, you should see:
```
✅ Consultation Completed Successfully!
Appointment completed successfully
Your appointment has been marked as completed.
[Return to Doctors Page buttons]
```

## 🚨 Emergency Workaround

If you need to test immediately without fixing the connection:

1. **Comment out the API call** in the Hugging Face script temporarily
2. **Show a success message** without actually completing the appointment
3. **Test the UI flow** while you fix the backend connection

This will let you test the user interface while you resolve the connection issue. 