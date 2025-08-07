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
from .news_service import NewsService
from .models import init_news_db, News, NewsCategory, NewsSubscription
from sqlalchemy import desc

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

# Initialize news service
news_service = NewsService()

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

@main.route('/complete_appointment_manual', methods=['GET', 'POST'])
@handle_error
def complete_appointment_manual():
    """Manual appointment completion page for users returning from Hugging Face."""
    
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id', '').strip()
        
        if not appointment_id:
            flash("Please enter an appointment ID", "error")
            return redirect(url_for('main.complete_appointment_manual'))
        
        # Try to complete the appointment
        try:
            # Get appointment
            doc_ref = db.collection('appointments').document(appointment_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                flash("Appointment not found. Please check the appointment ID.", "error")
                return redirect(url_for('main.complete_appointment_manual'))
                
            appointment_data = doc.to_dict()
            appointment_data['status'] = 'completed'
            appointment_data['completed_at'] = datetime.datetime.now().isoformat()
            
            # Move to completed appointments
            completed_ref = db.collection('completed_appointments').document(appointment_id)
            completed_ref.set(appointment_data)
            
            # Delete from active appointments
            doc_ref.delete()
            
            flash(f"Appointment {appointment_id} completed successfully!", "success")
            return redirect(url_for('main.doctors'))
            
        except Exception as e:
            flash(f"Error completing appointment: {str(e)}", "error")
            return redirect(url_for('main.complete_appointment_manual'))
    
    # GET request - show the form
    return render_template('complete_appointment_manual.html')

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

                # Log the saved file path
                logging.info(f"Report saved at: {report_filepath}")


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
@handle_error
def download_report(filename):
    try:
        # Log the filename being requested
        logging.info(f"Attempting to download file: {filename}")
        
        # Fix the file path construction
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        
        # Return the file with attachment disposition
        return send_from_directory(
            directory=UPLOAD_FOLDER,
            path=filename,
            as_attachment=True
        )
        
    except Exception as e:
        logging.error(f"Error in download_report: {str(e)}")
        return jsonify({'error': 'Error downloading file'}), 500

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/news')
def news():
    """Main news page with filtering and search capabilities"""
    try:
        # Get query parameters
        category = request.args.get('category', '')
        search_query = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        limit = 12
        offset = (page - 1) * limit
        
        # Get news articles
        if search_query:
            articles = news_service.search_news(search_query, limit=limit)
        elif category:
            articles = news_service.get_news_from_db(category=category, limit=limit, offset=offset)
        else:
            articles = news_service.get_news_from_db(limit=limit, offset=offset)
        
        # Get featured news
        featured_news = news_service.get_featured_news(limit=5)
        
        # Get categories
        categories = news_service.get_news_categories()
        
        # If no articles in database, fetch from API
        if not articles:
            articles = news_service.fetch_healthcare_news()
            if articles:
                news_service.save_news_to_db(articles)
        
        return render_template(
            'news.html',
            articles=articles,
            featured_news=featured_news,
            categories=categories,
            current_category=category,
            search_query=search_query,
            current_page=page
        )
    except Exception as e:
        logger.error(f"Error in news route: {e}")
        return render_template('news.html', articles=[], featured_news=[], categories=[])

@main.route('/news/<int:news_id>')
def news_detail(news_id):
    """News article detail page"""
    try:
        db = news_service.get_db_session()
        news = db.query(News).filter(News.id == news_id, News.is_active == True).first()
        
        if not news:
            flash('News article not found', 'error')
            return redirect(url_for('main.news'))
        
        # Increment read count
        news_service.increment_read_count(news_id)
        
        # Get related news
        related_news = db.query(News).filter(
            News.category == news.category,
            News.id != news_id,
            News.is_active == True
        ).order_by(desc(News.published_date)).limit(3).all()
        
        return render_template(
            'news_detail.html',
            news=news.to_dict(),
            related_news=[article.to_dict() for article in related_news]
        )
    except Exception as e:
        logger.error(f"Error in news_detail route: {e}")
        flash('Error loading news article', 'error')
        return redirect(url_for('main.news'))
    finally:
        db.close()

@main.route('/api/news')
def api_news():
    """API endpoint for news articles"""
    try:
        category = request.args.get('category', '')
        search_query = request.args.get('search', '')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        if search_query:
            articles = news_service.search_news(search_query, limit=limit)
        elif category:
            articles = news_service.get_news_from_db(category=category, limit=limit, offset=offset)
        else:
            articles = news_service.get_news_from_db(limit=limit, offset=offset)
        
        return jsonify({
            'status': 'success',
            'articles': articles,
            'total': len(articles)
        })
    except Exception as e:
        logger.error(f"Error in api_news: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/api/news/featured')
def api_featured_news():
    """API endpoint for featured news"""
    try:
        featured_news = news_service.get_featured_news(limit=5)
        return jsonify({
            'status': 'success',
            'articles': featured_news
        })
    except Exception as e:
        logger.error(f"Error in api_featured_news: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/api/news/categories')
def api_news_categories():
    """API endpoint for news categories"""
    try:
        categories = news_service.get_news_categories()
        return jsonify({
            'status': 'success',
            'categories': categories
        })
    except Exception as e:
        logger.error(f"Error in api_news_categories: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/api/news/search')
def api_news_search():
    """API endpoint for news search"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'status': 'error', 'message': 'Search query required'}), 400
        
        articles = news_service.search_news(query, limit=20)
        return jsonify({
            'status': 'success',
            'articles': articles,
            'query': query,
            'total': len(articles)
        })
    except Exception as e:
        logger.error(f"Error in api_news_search: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/api/news/subscribe', methods=['POST'])
def api_news_subscribe():
    """API endpoint for newsletter subscription"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        categories = data.get('categories', [])
        
        if not email:
            return jsonify({'status': 'error', 'message': 'Email is required'}), 400
        
        success = news_service.subscribe_to_newsletter(email, categories)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Successfully subscribed to newsletter'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to subscribe to newsletter'
            }), 500
    except Exception as e:
        logger.error(f"Error in api_news_subscribe: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/api/news/fetch', methods=['POST'])
def api_fetch_news():
    """API endpoint to fetch fresh news from external APIs"""
    try:
        category = request.json.get('category', 'health')
        page_size = request.json.get('page_size', 20)
        
        articles = news_service.fetch_healthcare_news(category=category, page_size=page_size)
        
        if articles:
            success = news_service.save_news_to_db(articles)
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'Successfully fetched and saved {len(articles)} articles',
                    'articles_count': len(articles)
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to save articles to database'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'No articles fetched'
            }), 404
    except Exception as e:
        logger.error(f"Error in api_fetch_news: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/news/refresh', methods=['POST'])
@handle_error
def refresh_news():
    """Refresh news from external APIs"""
    try:
        articles = news_service.fetch_healthcare_news()
        if articles:
            success = news_service.save_news_to_db(articles)
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'Successfully refreshed {len(articles)} news articles',
                    'articles_count': len(articles)
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to save news articles'
                }), 500
        else:
            return jsonify({
                'status': 'info',
                'message': 'No new articles found'
            }), 200
    except Exception as e:
        logger.error(f"Error in refresh_news: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error refreshing news'
        }), 500

@main.route('/news/category/<category>')
def news_by_category(category):
    """News filtered by category"""
    try:
        page = int(request.args.get('page', 1))
        limit = 12
        offset = (page - 1) * limit
        
        articles = news_service.get_news_from_db(category=category, limit=limit, offset=offset)
        categories = news_service.get_news_categories()
        
        return render_template(
            'news.html',
            articles=articles,
            categories=categories,
            current_category=category,
            current_page=page
        )
    except Exception as e:
        logger.error(f"Error in news_by_category: {e}")
        return redirect(url_for('main.news'))

@main.route('/news/search')
def news_search():
    """News search page"""
    try:
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        limit = 12
        offset = (page - 1) * limit
        
        if query:
            articles = news_service.search_news(query, limit=limit)
        else:
            articles = []
        
        categories = news_service.get_news_categories()
        
        return render_template(
            'news.html',
            articles=articles,
            categories=categories,
            search_query=query,
            current_page=page
        )
    except Exception as e:
        logger.error(f"Error in news_search: {e}")
        return redirect(url_for('main.news'))

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