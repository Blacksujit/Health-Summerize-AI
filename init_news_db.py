#!/usr/bin/env python3
"""
Script to initialize the news database and add sample data
"""

import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import init_news_db, News, NewsCategory, NewsSubscription, Base
from sqlalchemy.orm import Session

def init_database():
    """Initialize the news database with sample data"""
    print("Initializing news database...")
    
    # Initialize database
    SessionLocal = init_news_db()
    db = SessionLocal()
    
    try:
        # Create sample categories
        categories = [
            {
                'name': 'COVID-19',
                'description': 'Latest updates on COVID-19 research, treatments, and vaccines',
                'color': '#FF6B6B',
                'icon': 'fa fa-virus'
            },
            {
                'name': 'AI in Medicine',
                'description': 'Artificial intelligence applications in healthcare',
                'color': '#4ECDC4',
                'icon': 'fa fa-robot'
            },
            {
                'name': 'Telemedicine',
                'description': 'Digital health and remote healthcare solutions',
                'color': '#45B7D1',
                'icon': 'fa fa-video'
            },
            {
                'name': 'Research',
                'description': 'Latest medical research and clinical trials',
                'color': '#96CEB4',
                'icon': 'fa fa-flask'
            },
            {
                'name': 'Mental Health',
                'description': 'Mental health and wellness news',
                'color': '#FFEAA7',
                'icon': 'fa fa-brain'
            }
        ]
        
        # Add categories
        for cat_data in categories:
            existing = db.query(NewsCategory).filter(NewsCategory.name == cat_data['name']).first()
            if not existing:
                category = NewsCategory(**cat_data)
                db.add(category)
                print(f"Added category: {cat_data['name']}")
        
        # Create sample news articles
        sample_articles = [
            {
                'title': 'AI Predicts New COVID-19 Variants with Unprecedented Accuracy',
                'content': 'Researchers leverage advanced AI models to forecast emerging coronavirus variants, enabling faster global response and vaccine adaptation. The new system analyzes genetic sequences and epidemiological data to predict which variants are most likely to spread.',
                'summary': 'AI models are revolutionizing COVID-19 variant prediction.',
                'source': 'HealthTech News',
                'url': '#',
                'image_url': '/static/images/news-img.png',
                'category': 'COVID-19',
                'tags': 'AI,COVID-19,Research,Vaccines',
                'published_date': datetime.now(),
                'sentiment_score': 0.2,
                'ai_generated': False,
                'is_featured': True
            },
            {
                'title': 'Virtual Consultations Surge: Telemedicine Becomes Mainstream',
                'content': 'The adoption of telemedicine has skyrocketed, with AI-driven platforms ensuring secure, efficient, and accessible healthcare for all. Patients can now receive quality care from the comfort of their homes.',
                'summary': 'Telemedicine adoption reaches new heights with AI integration.',
                'source': 'Digital Health Today',
                'url': '#',
                'image_url': '/static/images/Virtual-consultation.jpeg',
                'category': 'Telemedicine',
                'tags': 'Telemedicine,AI,Digital Health',
                'published_date': datetime.now(),
                'sentiment_score': 0.4,
                'ai_generated': False,
                'is_featured': True
            },
            {
                'title': 'AI Summarizes EHRs: Doctors Save Hours Weekly',
                'content': 'New AI tools are transforming electronic health records into concise, actionable insights, freeing up valuable time for clinicians and improving patient care. The system can process thousands of pages of medical records in minutes.',
                'summary': 'AI-powered EHR summarization improves clinical efficiency.',
                'source': 'Medical AI Weekly',
                'url': '#',
                'image_url': '/static/images/AI-summerizer.jpeg',
                'category': 'AI in Medicine',
                'tags': 'AI,EHR,Clinical',
                'published_date': datetime.now(),
                'sentiment_score': 0.6,
                'ai_generated': False,
                'is_featured': True
            },
            {
                'title': 'AI Detects Early Signs of Heart Disease from Wearables',
                'content': 'A breakthrough in wearable tech: AI algorithms now detect subtle heart irregularities, empowering patients and clinicians with real-time insights. This technology could save thousands of lives through early detection.',
                'summary': 'Wearable AI technology advances heart disease detection.',
                'source': 'Cardiology Today',
                'url': '#',
                'image_url': '/static/images/Heart-disease.jpeg',
                'category': 'AI in Medicine',
                'tags': 'AI,Wearables,Cardiology',
                'published_date': datetime.now(),
                'sentiment_score': 0.5,
                'ai_generated': False,
                'is_featured': False
            },
            {
                'title': 'Mental Health Apps Show Promise in Clinical Trials',
                'content': 'Digital mental health applications are showing significant promise in clinical trials, with AI-powered therapy tools demonstrating effectiveness comparable to traditional therapy methods.',
                'summary': 'Digital mental health tools prove effective in clinical studies.',
                'source': 'Mental Health Weekly',
                'url': '#',
                'image_url': '/static/images/Mental-health.jpeg',
                'category': 'Mental Health',
                'tags': 'Mental Health,Apps,Clinical Trials',
                'published_date': datetime.now(),
                'sentiment_score': 0.3,
                'ai_generated': False,
                'is_featured': False
            }
        ]
        
        # Add sample articles
        for article_data in sample_articles:
            existing = db.query(News).filter(News.title == article_data['title']).first()
            if not existing:
                article = News(**article_data)
                db.add(article)
                print(f"Added article: {article_data['title']}")
        
        # Commit all changes
        db.commit()
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 