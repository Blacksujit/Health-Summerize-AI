
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
# from PyQt5.QtWebEngineWidgets import QApplication
# from PyQt5.QtCore import QUrl
# from .second_utility import create_scenario_based_infographic_video , create_animated_pie_chart , parse_user_input , generate_audio_from_text, generate_narration, add_auto_generated_audio_to_video
# from  .text_processing import nlp_pipeline
# from  .gif_animation_creation import create_animated_gif
# from  .data_storytelling_video_processing import convert_gif_to_storytelling_video
# from flask import Blueprint
# video_processing = Blueprint('video_processing', __name__)

main = Blueprint('main', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants and configurations
BASE_DIR = Path(__file__).resolve().parent
# Define path for static folder to serve video
# UPLOADS_FOLDER = os.path.join(os.getcwd(), 'uploads', 'videos')
# All the routes will be displayed Here means defined here 



# Route for the Index Page
@main.route('/')
def index():
    return render_template('index.html')  # Your index page template

# Route for the Protect Page
@main.route('/summerize')
def summerize():
    return render_template('summerize.html')  # Make sure to create 'protect.html'

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