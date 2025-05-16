
import http
import json
from flask import Blueprint, render_template, request, jsonify , send_file , send_from_directory , url_for
import logging
import os
import shutil
import time
import uuid
from flask import Blueprint, render_template, request, jsonify, send_file, send_from_directory, url_for
from werkzeug.utils import secure_filename
import os
import logging
import uuid
import time
import shutil
from functools import wraps
from pathlib import Path
from werkzeug.utils import secure_filename
import os
import datetime
from pathlib import Path
import mimetypes
from flask import session
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from .utility_script import MedicalNLPipeline
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from .__init__ import db , socketio # Import Firestore database instance
from flask_socketio import SocketIO, emit
import openai
from google.cloud import speech
import requests
import os
import openai
import whisper
# from elevenlabs import generate, save
from flask import Flask, request, jsonify , Response
from flask_socketio import SocketIO 
import subprocess
import logging
# from elevenlabs import text_to_speech, save
from flask_cors import CORS
import http.client


 
# # Set your API keys
# openai.api_key = "yur_apiKey"
# elevenlabs_api_key = "yur_api_key"



main = Blueprint('main', __name__)

CORS(main, resources={r"/*": {"origins": "*"}})
# Set OpenAI API Key
# openai.api_key = "yur_api_key"  # Replace with your OpenAI API key
# # Whisper model
# whisper_model = whisper.load_model("base")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





# Constants and configurations
BASE_DIR = Path(__file__).resolve().parent
# Define path for static folder to serve video
# UPLOADS_FOLDER = os.path.join(os.getcwd(), 'uploads', 'videos')
# All the routes will be displayed Here means defined here 

# Configure file upload settings
UPLOAD_FOLDER = 'C:\\Users\\HP\\OneDrive\\Desktop\\Machine Learning Projects\\Health-Summerize-AI\\uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'json'}
# Define the base directory for the video files
VIDEO_DIRECTORY = os.path.abspath(os.path.join(BASE_DIR, 'static', 'avatar-videos'))

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Utility to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route for the Index Page
@main.route('/')
def index():
    return render_template('index.html')  # Your index page template




# @main.route('/ai_doctor_chat', methods=['POST'])
# def ai_doctor_chat():
#     """
#     Handles communication with the AI Doctor API.
#     """
#     try:
#         # Get the user message and appointment details from the request
#         data = request.get_json()
#         user_message = data.get('message', '').strip()
#         specialization = data.get('specialization', 'general')
#         language = data.get('language', 'en')

#         if not user_message:
#             return jsonify({'status': 'error', 'message': 'Message is required'}), 400

#         # Prepare the API request
#         conn = http.client.HTTPSConnection("ai-doctor-api-ai-medical-chatbot-healthcare-ai-assistant.p.rapidapi.com")
#         payload = json.dumps({
#             "message": user_message,
#             "specialization": specialization,
#             "language": language
#         })
#         headers = {
#             'x-rapidapi-key': "2408f98dfemshf58df2f19cfc556p1a26c5jsnac7fa5db12ad",
#             'x-rapidapi-host': "ai-doctor-api-ai-medical-chatbot-healthcare-ai-assistant.p.rapidapi.com",
#             'Content-Type': "application/json"
#         }

#         # Send the request to the AI Doctor API
#         conn.request("POST", "/chat?noqueue=1", payload, headers)
#         res = conn.getresponse()
#         data = res.read()

#         # Parse the API response
#         response_data = json.loads(data.decode("utf-8"))
#         return jsonify({'status': 'success', 'response': response_data})
#     except Exception as e:
#         logging.error(f"Error in AI Doctor Chat: {str(e)}")
#         return jsonify({'status': 'error', 'message': 'Server error occurred'}), 500    
    
@main.route('/doctors', methods=['GET'])
def doctors():
    try:
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
    except Exception as e:
        logging.error(f"Error fetching appointments: {str(e)}")
        flash("Error loading appointments", "error")
        return render_template('doctors.html', appointments=[], completed_appointments=[])
    
# Route for Booking an Appointment
@main.route('/book', methods=['POST'])
def book():
    try:
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
            logging.error(f"Invalid date and time format: {time_str}")
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
    
    except Exception as e:
        logging.error(f"Booking error: {str(e)}")
        flash("Error booking appointment. Please try again.", "error")
        return redirect(url_for('main.doctors'))
        
@main.route('/get_appointments', methods=['GET'])
def get_appointments():
    try:
        # Fetch active appointments
        appointments_ref = db.collection('appointments')
        appointments = [doc.to_dict() for doc in appointments_ref.stream()]

        return jsonify({
            'status': 'success',
            'appointments': appointments
        })
    except Exception as e:
        logging.error(f"Error fetching appointments: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Error fetching appointments'}), 500
        
# Route for Validating Appointment ID
@main.route('/validate_appointment', methods=['POST'])
def validate_appointment():
    try:
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
    except Exception as e:
        logging.error(f"Validation error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error occurred'}), 500
    
                                
@main.route('/complete_appointment', methods=['POST'])
def complete_appointment():
    try:
        data = request.get_json()
        appointment_id = data.get('appointment_id', '').strip()

        if not appointment_id:
            return jsonify({'status': 'error', 'message': 'Appointment ID is required'}), 400

        # Fetch the appointment from the database
        doc_ref = db.collection('appointments').document(appointment_id)
        doc = doc_ref.get()

        if not doc.exists():
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

        # Move the appointment to the completed_appointments collection
        appointment_data = doc.to_dict()
        appointment_data['status'] = 'completed'
        appointment_data['completed_at'] = datetime.datetime.now().isoformat()

        db.collection('completed_appointments').document(appointment_id).set(appointment_data)

        # Delete the appointment from the active appointments collection
        doc_ref.delete()

        return jsonify({'status': 'success', 'message': 'Appointment marked as completed.'})
    except Exception as e:
        logging.error(f"Error completing appointment: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error occurred'}), 500    
    
                        
@main.route('/virtual_consultation_voice/<appointment_id>')
def virtual_consultation_voice(appointment_id):
    try:
        # Fetch the appointment from the database
        doc_ref = db.collection('appointments').document(appointment_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            flash("Invalid or expired appointment.", "error")
            logging.error(f"Appointment ID {appointment_id} does not exist.")
            return redirect(url_for('main.doctors'))
        
        # Validate appointment time
        appointment_data = doc.to_dict()
        try:
            appointment_time = datetime.datetime.strptime(appointment_data['time'], '%B %d, %Y at %I:%M %p')
        except ValueError as e:
            flash("Invalid appointment time format.", "error")
            logging.error(f"Error parsing appointment time for ID {appointment_id}: {str(e)}")
            return redirect(url_for('main.doctors'))
        
        current_time = datetime.datetime.now()
        if appointment_time.date() != current_time.date():
            flash("This appointment is not scheduled for today.", "error")
            logging.warning(f"Appointment ID {appointment_id} is not scheduled for today.")
            return redirect(url_for('main.doctors'))
        
        # Render the consultation page
        return render_template(
            'virtual_consultation_voice.html',
            appointment_id=appointment_id,
            appointment_data=appointment_data,
            now=current_time
        )
    except Exception as e:
        logging.error(f"Error rendering consultation page for ID {appointment_id}: {str(e)}")
        flash("Error starting consultation.", "error")
        return redirect(url_for('main.doctors'))
                            
@main.route('/summerize', methods=['GET', 'POST'])
def summerize():
    if request.method == 'POST':
        file = request.files.get('file')
        text_input = request.form.get('text')
        medical_nlp = MedicalNLPipeline()

        try:
            result = None

            # Validate input
            if file and allowed_file(file.filename):
                # Save the uploaded file
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                # Process the uploaded file
                result = medical_nlp.process_document(file_path=filepath)

            elif text_input:
                # Process the entered text
                result = medical_nlp.process_document(prompt=text_input)

            else:
                flash('Please provide a valid file or text input for summarization.')
                return redirect(url_for('main.summerize'))

            if result:
                # Extract sentiment results
                sentiment_data = result.get('sentiment', {})
                sentiment_label = sentiment_data.get('label', 'Unknown')
                report = result.get('report', 'No structured report available.')
                sentiment_score = sentiment_data.get('score') or sentiment_data.get('confidence', 'N/A')

                # Save the report as a file
                report_filename = f"report_{uuid.uuid4().hex}.txt"  # Generate a unique filename
                report_filepath = os.path.join(UPLOAD_FOLDER, report_filename)
                with open(report_filepath, 'w') as f:
                    f.write(report)  # Save the report content to the file

                # Pass relevant data to the reports.html template
                return render_template(
                    'reports.html',
                    report=report,
                    sentiment_label=sentiment_label,
                    sentiment_score=sentiment_score,                    report_filename=report_filename  # Pass the filename to the template
                )

        except Exception as e:
            logging.error(f"Error in processing: {str(e)}")
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for('main.summerize'))

    # Render the summarize page
    return render_template('summerize.html')


@main.route('/Reports')
def Reports():
    return render_template('Reports.html')


@main.route('/download_report/<filename>')
def download_report(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


# Route for the About Page
@main.route('/about')
def about():
    return render_template('about.html')  # Make sure to create 'about.html'

# # Route for the Doctors Page
# @main.route('/doctors')
# def doctors():#     return render_template('doctors.html')  # Make sure to create 'doctors.html'

# Route for the News Page
@main.route('/news')
def news():
    return render_template('news.html')  # Make sure to create 'news.html'



@main.route('/serve_video/<filename>')
def serve_video(filename):
    try:
        # Construct the full path to the video file
        video_path = os.path.join(VIDEO_DIRECTORY, filename)
        
        # Log the resolved path for debugging
        logging.info(f"Resolved video path: {video_path}")
        
        # Check if the file exists
        if not os.path.exists(video_path):
            logging.error(f"Video file not found: {video_path}")
            return jsonify({'error': 'Video file not found'}), 404
        
        # Serve the video file
        return send_file(video_path, mimetype='video/mp4')
    except Exception as e:
        logging.error(f"Error serving video: {str(e)}")
        return Response("Error serving video", status=500)

@main.route('/debug_video_path')
def debug_video_path():
    # Debugging route to verify the resolved path
    video_path = os.path.join(VIDEO_DIRECTORY, 'doctorAIavatar.mp4')
    return jsonify({'resolved_path': video_path, 'exists': os.path.exists(video_path)})# @main.route('/upload_audio', methods=['POST'])
# def upload_audio():
#     try:
#         # Save uploaded audio
#         audio_file = request.files['audio']
#         audio_path = os.path.join("uploads", audio_file.filename)
#         audio_file.save(audio_path)

#         # Transcribe audio using Whisper
#         result = whisper_model.transcribe(audio_path)
#         transcription = result['text']

#         # Generate AI response using GPT
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[{"role": "user", "content": transcription}]
#         )
#         ai_response = response['choices'][0]['message']['content']

#         # Generate voice using Eleven Labs
#         voice_audio = text_to_speech(
#             text=ai_response,
#             voice="Rachel",  # Replace with your Eleven Labs voice
#             api_key=elevenlabs_api_key
#         )
#         voice_path = os.path.join("uploads", "response.mp3")
#         save(voice_audio, voice_path)

#         # Generate lip sync using Rhubarb
#         lipsync_path = os.path.join("uploads", "response.json")
#         subprocess.run(["rhubarb", voice_path, "-o", lipsync_path])

#         return jsonify({
#             "transcription": transcription,
#             "response_text": ai_response,
#             "voice_path": voice_path,
#             "lipsync_path": lipsync_path
#         })
#     except Exception as e:
#         logging.error(f"Error in /upload_audio: {e}")
#         return jsonify({"error": str(e)}), 500


