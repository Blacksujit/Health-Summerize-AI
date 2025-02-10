
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
import pdfkit
from pathlib import Path

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
# Path to wkhtmltopdf executable
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf="C:\\Downloads\\wkhtmltox-0.12.6-1.msvc2015-win64.exe")

# Utility to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route for the Index Page
@main.route('/')
def index():
    return render_template('index.html')  # Your index page template

# Route for the Protect Page

# Route for the Summarize Page
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

                # Pass relevant data to the reports.html template (excluding verbose summary)
                return render_template(
                    'reports.html',
                    report=report,
                    sentiment_label=sentiment_label,
                    sentiment_score=sentiment_score
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

@main.route('/download_report', methods=['POST'])
def download_report():
    report_content = request.form.get('report_content')
    sentiment_label = request.form.get('sentiment_label')
    sentiment_score = request.form.get('sentiment_score')

    rendered = render_template('Reports.html', report=report_content, sentiment_label=sentiment_label, sentiment_score=sentiment_score)
    pdf = pdfkit.from_string(rendered, False, configuration=PDFKIT_CONFIG)

    response = send_file(
        pdf,
        as_attachment=True,
        download_name='report.pdf',
        mimetype='application/pdf'
    )
    return response

# Route for the About Page
@main.route('/about')
def about():
    return render_template('about.html')  # Make sure to create 'about.html'

# Route for the Doctors Page
@main.route('/doctors')
def doctors():
    return render_template('doctors.html')  # Make sure to create 'doctors.html'

# Route for the News Page
@main.route('/news')
def news():
    return render_template('news.html')  # Make sure to create 'news.html'