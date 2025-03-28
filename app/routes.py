
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
from .__init__ import db  # Import Firestore database instance


main = Blueprint('main', __name__)

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


    
# Route for the Doctors Page
# Route for the Doctors Page
@main.route('/doctors', methods=['GET'])
def doctors():
    # Fetch all appointments from Firebase Firestore
    appointments_ref = db.collection('appointments')
    appointments = [doc.to_dict() for doc in appointments_ref.stream()]

    return render_template('doctors.html', appointments=appointments)

# Route for Booking an Appointment
@main.route('/book', methods=['POST'])
def book():
    doctor = request.form['doctor']
    patient = request.form['patient']
    time = request.form['time']
    appointment_id = str(uuid.uuid4())  # Generate a unique appointment ID

    # Save appointment to Firebase Firestore
    appointment_data = {
        'doctor': doctor,
        'patient': patient,
        'time': time,
        'appointment_id': appointment_id
    }
    db.collection('appointments').document(appointment_id).set(appointment_data)

    flash(f'Appointment booked successfully! Your appointment ID is {appointment_id}', 'success')
    return redirect(url_for('main.doctors'))

# Route for Validating Appointment ID
@main.route('/validate_appointment', methods=['POST'])
def validate_appointment():
    data = request.get_json()  # Parse JSON data from the request
    appointment_id = data.get('appointment_id')

    if not appointment_id:
        return jsonify({'status': 'error', 'message': 'Appointment ID is required'}), 400

    # Check if the appointment exists in Firebase Firestore
    appointment_ref = db.collection('appointments').document(appointment_id)
    appointment = appointment_ref.get()

    if appointment.exists:
        return jsonify({'status': 'success', 'appointment': appointment.to_dict()})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid appointment ID'})
# Route for the Protect Page

@main.route('/virtual_consultation_voice/<appointment_id>')
def virtual_consultation_voice(appointment_id):
    return render_template('virtual_consultation_voice.html', appointment_id=appointment_id)

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
                    sentiment_score=sentiment_score,
                    report_filename=report_filename  # Pass the filename to the template
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
# def doctors():
#     return render_template('doctors.html')  # Make sure to create 'doctors.html'

# Route for the News Page
@main.route('/news')
def news():
    return render_template('news.html')  # Make sure to create 'news.html'