# Environment Variables Setup Guide

This guide will help you set up and use environment variables in your Medivance application.

## 🎯 **What are Environment Variables?**

Environment variables are key-value pairs that store configuration settings outside of your code. They're perfect for:
- ✅ Storing sensitive information (API keys, passwords)
- ✅ Managing different configurations for development/production
- ✅ Keeping secrets out of your code repository
- ✅ Making your application more secure and flexible

## 📁 **File Structure**

```
AI-Health-Summerize/
├── .env                    # Your actual environment variables (NOT in git)
├── env.example            # Example environment file (safe to commit)
├── .gitignore             # Already configured to ignore .env
└── app/
    ├── __init__.py        # Loads environment variables
    ├── news_service.py    # Uses environment variables
    └── routes.py          # Uses environment variables
```

## 🚀 **Step-by-Step Setup**

### 1. **Create Your Environment File**

```bash
# Copy the example file to create your .env file
cp env.example .env
```

### 2. **Edit Your .env File**

Open the `.env` file and replace the placeholder values with your actual API keys and configuration:

```bash
# Example .env file
NEWS_API_KEY=your_actual_news_api_key_here
OPENAI_API_KEY=your_actual_openai_api_key_here
RAPIDAPI_KEY=your_actual_rapidapi_key_here
SECRET_KEY=your_generated_secret_key_here
DEBUG=True
FLASK_ENV=development
```

### 3. **Generate a Secret Key**

You can generate a secure secret key using Python:

```python
import secrets
print(secrets.token_hex(32))
```

Or use this command:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🔑 **Required API Keys**

### **NewsAPI Key**
1. Go to [https://newsapi.org/](https://newsapi.org/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add it to your `.env` file:
   ```
   NEWS_API_KEY=your_news_api_key_here
   ```

### **OpenAI API Key**
1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Sign up and get your API key
3. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### **RapidAPI Key** (Optional)
1. Go to [https://rapidapi.com/](https://rapidapi.com/)
2. Sign up and get your API key
3. Add it to your `.env` file:
   ```
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```

## 💻 **How to Use Environment Variables in Code**

### **1. Loading Environment Variables**

Your application already loads environment variables in `app/__init__.py`:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now you can access environment variables
api_key = os.getenv('NEWS_API_KEY', 'default_value')
```

### **2. Accessing Environment Variables**

```python
import os

# Get environment variable with default value
api_key = os.getenv('NEWS_API_KEY', '')

# Get environment variable (returns None if not found)
debug_mode = os.getenv('DEBUG')

# Get environment variable and convert to boolean
debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'

# Get environment variable and convert to integer
port = int(os.getenv('PORT', '5000'))
```

### **3. Example Usage in Your Code**

```python
# In app/news_service.py
class NewsService:
    def __init__(self):
        self.api_keys = {
            'newsapi': os.getenv('NEWS_API_KEY', ''),
            'rapidapi': os.getenv('RAPIDAPI_KEY', ''),
            'openai': os.getenv('OPENAI_API_KEY', '')
        }
    
    def fetch_news(self):
        if not self.api_keys['newsapi']:
            logger.warning("NewsAPI key not found, using mock data")
            return self._get_mock_news()
        # ... rest of the code
```

## 🔒 **Security Best Practices**

### **1. Never Commit .env Files**

Your `.gitignore` already includes:
```
.env
```

This ensures your sensitive information is never committed to version control.

### **2. Use Strong Secret Keys**

Generate a strong secret key:
```python
import secrets
secret_key = secrets.token_hex(32)
```

### **3. Validate Environment Variables**

```python
def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = ['NEWS_API_KEY', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Environment variables not loading**
   ```python
   # Make sure you have this at the top of your file
   from dotenv import load_dotenv
   load_dotenv()
   ```

2. **File not found error**
   ```bash
   # Make sure .env file exists in the root directory
   ls -la .env
   ```

3. **Permission issues**
   ```bash
   # Check file permissions
   chmod 600 .env
   ```

### **Debug Environment Variables**

```python
import os

# Print all environment variables (for debugging)
for key, value in os.environ.items():
    if 'API' in key or 'KEY' in key:
        print(f"{key}: {value[:10]}..." if value else f"{key}: Not set")
```

## 🚀 **Production Deployment**

### **1. Production Environment Variables**

For production, set environment variables directly on your server:

```bash
# Set environment variables
export NEWS_API_KEY="your_production_key"
export SECRET_KEY="your_production_secret"
export DEBUG="False"
export FLASK_ENV="production"
```

### **2. Using a .env.production File**

Create a separate production environment file:

```bash
# .env.production
NEWS_API_KEY=your_production_news_api_key
OPENAI_API_KEY=your_production_openai_key
SECRET_KEY=your_production_secret_key
DEBUG=False
FLASK_ENV=production
```

### **3. Docker Environment Variables**

If using Docker, you can pass environment variables:

```dockerfile
# Dockerfile
ENV NEWS_API_KEY=your_key_here
ENV SECRET_KEY=your_secret_here
```

Or use docker-compose:

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - NEWS_API_KEY=${NEWS_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
```

## 📋 **Environment Variables Checklist**

- [ ] Created `.env` file from `env.example`
- [ ] Added your actual API keys
- [ ] Generated a secure `SECRET_KEY`
- [ ] Set `DEBUG` and `FLASK_ENV` appropriately
- [ ] Verified `.env` is in `.gitignore`
- [ ] Tested that environment variables are loading correctly

## 🎯 **Quick Start Commands**

```bash
# 1. Copy example file
cp env.example .env

# 2. Edit .env file with your actual values
nano .env  # or use your preferred editor

# 3. Test environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('NEWS_API_KEY:', os.getenv('NEWS_API_KEY', 'Not set'))"

# 4. Run your application
python app.py
```

## 🔍 **Verification**

To verify your environment variables are working:

```python
# Create a test script: test_env.py
from dotenv import load_dotenv
import os

load_dotenv()

print("Environment Variables Test:")
print(f"NEWS_API_KEY: {'✓ Set' if os.getenv('NEWS_API_KEY') else '✗ Not set'}")
print(f"OPENAI_API_KEY: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Not set'}")
print(f"SECRET_KEY: {'✓ Set' if os.getenv('SECRET_KEY') else '✗ Not set'}")
print(f"DEBUG: {os.getenv('DEBUG', 'Not set')}")
```

Run it:
```bash
python test_env.py
```

## 🎉 **You're All Set!**

Your environment variables are now properly configured and secure. Your application will automatically load them when it starts, and your sensitive information is protected from being committed to version control.

Remember:
- ✅ Keep your `.env` file secure and never commit it
- ✅ Use strong, unique API keys
- ✅ Regularly rotate your keys
- ✅ Use different keys for development and production

Happy coding! 🚀 