
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

main = Blueprint('main', __name__)

# Set OpenAI API Key
openai.api_key = "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"  # Replace with your OpenAI API key

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
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Utility to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route for the Index Page
@main.route('/')
def index():
    return render_template('index.html')  # Your index page template


# Handle voice queries from the patient
@socketio.on('process_voice')
def handle_voice_query(data):
    try:
        appointment_id = data.get('appointment_id')
        audio_file_path = data.get('audio_file_path')

        # Use Google Cloud Speech-to-Text to transcribe the audio
        client = speech.SpeechClient()
        with open(audio_file_path, 'rb') as audio_file:
            audio_content = audio_file.read()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        )

        response = client.recognize(config=config, audio=audio)
        patient_message = response.results[0].alternatives[0].transcript

        # Generate AI doctor response using OpenAI GPT
        ai_response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"You are a helpful AI doctor. Patient says: {patient_message}",
            max_tokens=150,
            temperature=0.7
        ).choices[0].text.strip()

        # Send the response back to the frontend
        emit('ai_voice_response', {'response_text': ai_response})
    except Exception as e:
        print(f"Error processing voice query: {str(e)}")
        emit('ai_voice_response', {'response_text': 'Sorry, I encountered an error. Please try again.'})
    
# Route for the Doctors Page
# Route for the Doctors Page
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
        
        # Return success and redirect URL
        return jsonify({
            'status': 'success',
            'redirect_url': url_for('main.virtual_consultation_voice', appointment_id=appointment_id)
        })
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
        
        # Get and move appointment
        doc_ref = db.collection('appointments').document(appointment_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404
        
        # Update and move to completed
        appointment_data = doc.to_dict()
        appointment_data['status'] = 'completed'
        appointment_data['completed_at'] = datetime.datetime.now().isoformat()
        
        db.collection('completed_appointments').document(appointment_id).set(appointment_data)
        doc_ref.delete()
        
        return jsonify({'status': 'success', 'message': 'Appointment marked as completed.'})
        
    except Exception as e:
        logging.error(f"Completion error: {str(e)}")
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