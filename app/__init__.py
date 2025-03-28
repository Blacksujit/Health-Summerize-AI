from flask import Flask
from flask_caching import Cache
from flask import url_for
from flask_cors import CORS
import os
import sqlite3
import os 
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
# cred = credentials.Certificate("C:\\Users\\HP\\OneDrive\\Desktop\\openSource\\AI-Health-Summerize\\config\\water-management-91e4a-firebase-adminsdk-drmsv-dd559d16f2.json")  # Replace with your Firebase Admin SDK JSON file
# firebase_admin.initialize_app(cred)


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase only if it hasn't been initialized already
if not firebase_admin._apps:
    firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS")
    cred = credentials.Certificate(firebase_credentials_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()  # Firestore database instance

socketio = SocketIO()  # Initialize SocketIO


def init_db():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'appointments.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
        # Free up space by setting journal mode to MEMORY
    c.execute("PRAGMA journal_mode = MEMORY;")
    c.execute("PRAGMA temp_store = MEMORY;")
    
    c.execute('DROP TABLE IF EXISTS appointments')  # Drop the existing table if it exists
    c.execute('''CREATE TABLE appointments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, doctor TEXT, patient TEXT, time TEXT, appointment_id TEXT UNIQUE)''')
    conn.commit()
    conn.close()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')  # Specify the path to the templates and static folders
        # Initialize SocketIO
    socketio.init_app(app)
    # Set cache directory and other caching parameters
    # app.register_blueprint(main)  # Register Blueprint
    # ✅ Fix Hugging Face model cache storage
    os.environ["HUGGINGFACE_HUB_CACHE"] = "D:/cahc_models_folder"
    # models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    CORS(app)
    app.secret_key = 'blackshadow'  # Replace 'your_secret_key' with a strong, unique key
    app.config['CACHE_TYPE'] = 'filesystem'
    app.config['CACHE_DIR'] = 'D:\\cahc_models_folder'  # Change this to your desired cache path
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    app.config['SESSION_COOKIE_SECURE'] = False  # Use True in production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Initialize the cache
    cache = Cache(app)
    # Set the path for the models directory (outside the app directory)
    

    with app.app_context():
        from .routes import main
        app.register_blueprint(main)
    
    return app