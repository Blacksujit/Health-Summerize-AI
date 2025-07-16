import http
import json
import os
import logging
import uuid
import time
import shutil
import datetime
import mimetypes
from pathlib import Path
from functools import wraps
from flask import (
    Blueprint, render_template, request, jsonify, send_file,
    send_from_directory, url_for, session, flash, redirect, Response
)
from werkzeug.utils import secure_filename
import pandas as pd
import requests
import openai
from google.cloud import speech
import whisper
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv
from .__init__ import db, socketio
from .utility_script import MedicalNLPipeline

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
main = Blueprint('main', __name__)
CORS(main, resources={r"/*": {"origins": "*"}})

# Configure API keys from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

# Configure paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
VIDEO_DIRECTORY = BASE_DIR / 'static' / 'avatar-videos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'json'}

# Create necessary directories
UPLOAD_FOLDER.mkdir(exist_ok=True)
VIDEO_DIRECTORY.mkdir(exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_error(func):
    """Decorator for handling route errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return jsonify({'status': 'error', 'message': 'An error occurred'}), 500
    return wrapper

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/doctors', methods=['GET'])
@handle_error
def doctors():
    # Fetch active appointments
    appointments_ref = db.collection('appointments')
    appointments = [doc.to_dict() for doc in appointments_ref.stream()]
    
    # Fetch completed appointments
    completed_ref = db.collection('completed_appointments')
    completed_appointments = [doc.to_dict() for doc in completed_ref.stream()]
    
    return render_template(
        'doctors.html',
        appointments=appointments,
        completed_appointments=completed_appointments
    )

@main.route('/book', methods=['POST'])
@handle_error
def book():
    # Validate and format input
    doctor = request.form.get('doctor', '').strip()
    patient = request.form.get('patient', '').strip()
    time_str = request.form.get('time', '').strip()
    
    if not all([doctor, patient, time_str]):
        flash("All fields are required", "error")
        return redirect(url_for('main.doctors'))
    
    # Format datetime
    try:
        time_obj = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M')
        formatted_time = time_obj.strftime('%B %d, %Y at %I:%M %p')
    except ValueError:
        flash("Invalid date and time format", "error")
        return redirect(url_for('main.doctors'))
    
    # Create appointment
    appointment_id = str(uuid.uuid4())
    appointment_data = {
        'doctor': doctor,
        'patient': patient,
        'time': formatted_time,
        'appointment_id': appointment_id,
        'status': 'scheduled',
        'created_at': datetime.datetime.now().isoformat()
    }
    
    # Save to Firestore
    db.collection('appointments').document(appointment_id).set(appointment_data)
    
    flash(f"Appointment booked successfully! Your ID: {appointment_id}", "success")
    return redirect(url_for('main.doctors'))

@main.route('/get_appointments', methods=['GET'])
@handle_error
def get_appointments():
    appointments_ref = db.collection('appointments')
    appointments = [doc.to_dict() for doc in appointments_ref.stream()]
    return jsonify({'status': 'success', 'appointments': appointments})

@main.route('/validate_appointment', methods=['POST'])
@handle_error
def validate_appointment():
    data = request.get_json()
    appointment_id = data.get('appointment_id', '').strip()

    if not appointment_id:
        return jsonify({'status': 'error', 'message': 'Appointment ID is required'}), 400

    # Check active appointments
    doc_ref = db.collection('appointments').document(appointment_id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({'status': 'error', 'message': 'Invalid or expired appointment ID'}), 404

    # Check appointment status and time
    appointment_data = doc.to_dict()
    appointment_time = datetime.datetime.strptime(appointment_data['time'], '%B %d, %Y at %I:%M %p')
    current_time = datetime.datetime.now()

    if appointment_time.date() != current_time.date():
        return jsonify({'status': 'error', 'message': 'This appointment is not scheduled for today'}), 400

    if appointment_data.get('status') != 'scheduled':
        return jsonify({'status': 'error', 'message': 'This appointment is not active'}), 400

    # Redirect to Hugging Face Spaces
    hugging_face_url = f"https://huggingface.co/spaces/blackshadow1/Multi-Modal-Medical-Analysis-System?appointment_id={appointment_id}"
    return jsonify({'status': 'success', 'redirect_url': hugging_face_url})

@main.route('/complete_appointment', methods=['POST'])
@handle_error
def complete_appointment():
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    
    if not appointment_id:
        return jsonify({'status': 'error', 'message': 'Appointment ID is required'}), 400
        
    # Get appointment
    doc_ref = db.collection('appointments').document(appointment_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404
        
    appointment_data = doc.to_dict()
    appointment_data['status'] = 'completed'
    appointment_data['completed_at'] = datetime.datetime.now().isoformat()
    
    # Move to completed appointments
    completed_ref = db.collection('completed_appointments').document(appointment_id)
    completed_ref.set(appointment_data)
    
    # Delete from active appointments
    doc_ref.delete()
    
    return jsonify({'status': 'success', 'message': 'Appointment completed successfully'})

@main.route('/virtual_consultation_voice/<appointment_id>')
@handle_error
def virtual_consultation_voice(appointment_id):
    # Fetch the appointment from the database
    doc_ref = db.collection('appointments').document(appointment_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        flash("Invalid or expired appointment.", "error")
        return redirect(url_for('main.doctors'))
    
    # Validate appointment time
    appointment_data = doc.to_dict()
    try:
        appointment_time = datetime.datetime.strptime(appointment_data['time'], '%B %d, %Y at %I:%M %p')
    except ValueError as e:
        flash("Invalid appointment time format.", "error")
        return redirect(url_for('main.doctors'))
    
    current_time = datetime.datetime.now()
    if appointment_time.date() != current_time.date():
        flash("This appointment is not scheduled for today.", "error")
        return redirect(url_for('main.doctors'))
    
    # Render the consultation page
    return render_template(
        'virtual_consultation_voice.html',
        appointment_id=appointment_id,
        appointment_data=appointment_data,
        now=current_time
    )

@main.route('/summerize', methods=['GET', 'POST'])
@handle_error
def summerize():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = UPLOAD_FOLDER / filename
            file.save(filepath)
            
            # Process the file
            pipeline = MedicalNLPipeline()
            summary = pipeline.process_document(str(filepath))
            
            return render_template('summerize.html', summary=summary)
            
    return render_template('summerize.html')

@main.route('/Reports')
def Reports():
    return render_template('Reports.html')

@main.route('/download_report/<filename>')
@handle_error
def download_report(filename):
    return send_from_directory('outputs', filename)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/news')
def news():
    return render_template('news.html')

@main.route('/serve_video/<filename>')
@handle_error
def serve_video(filename):
    try:
        video_path = VIDEO_DIRECTORY / filename
        if not video_path.exists():
            return jsonify({'error': 'Video not found'}), 404
            
        return send_file(str(video_path), mimetype='video/mp4')
    except Exception as e:
        logger.error(f"Error serving video {filename}: {e}")
        return jsonify({'error': 'Error serving video'}), 500

@main.route('/debug_video_path')
def debug_video_path():
    """Debugging route to verify the resolved path."""
    return jsonify({
        'video_directory': str(VIDEO_DIRECTORY),
        'exists': VIDEO_DIRECTORY.exists(),
        'is_dir': VIDEO_DIRECTORY.is_dir() if VIDEO_DIRECTORY.exists() else False
    })


