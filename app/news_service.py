import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from .models import News, NewsCategory, NewsSubscription, init_news_db, Base
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import re
from textblob import TextBlob
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.api_keys = {
            'newsapi': os.getenv('NEWS_API_KEY', ''),
            'rapidapi': os.getenv('RAPIDAPI_KEY', ''),
            'openai': os.getenv('OPENAI_API_KEY', '')
        }
        self.SessionLocal = init_news_db()
        
    def get_db_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def fetch_healthcare_news(self, category: str = 'health', page_size: int = 20) -> List[Dict]:
        """Fetch healthcare news from NewsAPI"""
        try:
            if not self.api_keys['newsapi']:
                logger.warning("NewsAPI key not found, using mock data")
                return self._get_mock_news()
            
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'us',
                'category': category,
                'pageSize': page_size,
                'apiKey': self.api_keys['newsapi'],
                'q': 'healthcare OR medical OR medicine OR health'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            processed_articles = []
            for article in articles:
                processed_article = self._process_article(article)
                if processed_article:
                    processed_articles.append(processed_article)
            
            return processed_articles
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return self._get_mock_news()
    
    def _process_article(self, article: Dict) -> Optional[Dict]:
        """Process and clean article data"""
        try:
            # Extract and clean content
            content = article.get('content', '') or article.get('description', '')
            if content:
                # Remove source attribution and clean content
                content = re.sub(r'\[.*?\]', '', content)
                content = re.sub(r'\(.*?\)', '', content)
                content = content.strip()
            
            # Generate summary if content is available
            summary = self._generate_summary(content) if content else None
            
            # Analyze sentiment
            sentiment_score = self._analyze_sentiment(content) if content else None
            
            return {
                'title': article.get('title', '').strip(),
                'content': content,
                'summary': summary,
                'source': article.get('source', {}).get('name', 'Unknown'),
                'url': article.get('url', ''),
                'image_url': article.get('urlToImage', ''),
                'category': 'Healthcare',
                'tags': self._extract_tags(article.get('title', '') + ' ' + content),
                'published_date': article.get('publishedAt'),
                'sentiment_score': sentiment_score,
                'ai_generated': False
            }
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            return None
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a summary of the content"""
        try:
            if len(content) <= max_length:
                return content
            
            # Simple summary generation (can be enhanced with AI)
            sentences = content.split('.')
            summary = '. '.join(sentences[:2]) + '.'
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + '...'
            
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return content[:max_length] + '...' if len(content) > max_length else content
    
    def _analyze_sentiment(self, text: str) -> Optional[float]:
        """Analyze sentiment of the text"""
        try:
            if not text:
                return None
            
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return None
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text"""
        try:
            # Common healthcare keywords
            healthcare_keywords = [
                'covid', 'vaccine', 'treatment', 'diagnosis', 'research', 'clinical',
                'patient', 'doctor', 'hospital', 'medicine', 'drug', 'therapy',
                'surgery', 'prevention', 'wellness', 'mental health', 'telemedicine',
                'AI', 'artificial intelligence', 'machine learning', 'digital health'
            ]
            
            text_lower = text.lower()
            found_tags = []
            
            for keyword in healthcare_keywords:
                if keyword in text_lower:
                    found_tags.append(keyword.title())
            
            return found_tags[:5]  # Limit to 5 tags
        except Exception as e:
            logger.error(f"Error extracting tags: {e}")
            return []
    
    def _get_mock_news(self) -> List[Dict]:
        """Return mock news data when API is not available"""
        return [
            {
                'title': 'AI Predicts New COVID-19 Variants with Unprecedented Accuracy',
                'content': 'Researchers leverage advanced AI models to forecast emerging coronavirus variants, enabling faster global response and vaccine adaptation.',
                'summary': 'AI models are revolutionizing COVID-19 variant prediction.',
                'source': 'HealthTech News',
                'url': '#',
                'image_url': '/static/images/news-img.png',
                'category': 'COVID-19',
                'tags': ['AI', 'COVID-19', 'Research'],
                'published_date': datetime.now().isoformat(),
                'sentiment_score': 0.2,
                'ai_generated': False
            },
            {
                'title': 'Virtual Consultations Surge: Telemedicine Becomes Mainstream',
                'content': 'The adoption of telemedicine has skyrocketed, with AI-driven platforms ensuring secure, efficient, and accessible healthcare for all.',
                'summary': 'Telemedicine adoption reaches new heights with AI integration.',
                'source': 'Digital Health Today',
                'url': '#',
                'image_url': '/static/images/news-img2.png',
                'category': 'Telemedicine',
                'tags': ['Telemedicine', 'AI', 'Digital Health'],
                'published_date': datetime.now().isoformat(),
                'sentiment_score': 0.4,
                'ai_generated': False
            },
            {
                'title': 'AI Summarizes EHRs: Doctors Save Hours Weekly',
                'content': 'New AI tools are transforming electronic health records into concise, actionable insights, freeing up valuable time for clinicians and improving patient care.',
                'summary': 'AI-powered EHR summarization improves clinical efficiency.',
                'source': 'Medical AI Weekly',
                'url': '#',
                'image_url': '/static/images/news-img3.png',
                'category': 'AI in Medicine',
                'tags': ['AI', 'EHR', 'Clinical'],
                'published_date': datetime.now().isoformat(),
                'sentiment_score': 0.6,
                'ai_generated': False
            },
            {
                'title': 'AI Detects Early Signs of Heart Disease from Wearables',
                'content': 'A breakthrough in wearable tech: AI algorithms now detect subtle heart irregularities, empowering patients and clinicians with real-time insights.',
                'summary': 'Wearable AI technology advances heart disease detection.',
                'source': 'Cardiology Today',
                'url': '#',
                'image_url': '/static/images/news-img4.png',
                'category': 'Cardiology',
                'tags': ['AI', 'Wearables', 'Cardiology'],
                'published_date': datetime.now().isoformat(),
                'sentiment_score': 0.5,
                'ai_generated': False
            }
        ]
    
    def save_news_to_db(self, news_data: List[Dict]) -> bool:
        """Save news articles to database"""
        try:
            db = self.get_db_session()
            
            for article_data in news_data:
                # Check if article already exists
                existing = db.query(News).filter(
                    News.title == article_data['title'],
                    News.source == article_data['source']
                ).first()
                
                if not existing:
                    news = News(**article_data)
                    db.add(news)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving news to database: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_news_from_db(self, category: str = None, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get news articles from database"""
        try:
            db = self.get_db_session()
            
            query = db.query(News).filter(News.is_active == True)
            
            if category:
                query = query.filter(News.category == category)
            
            articles = query.order_by(desc(News.published_date)).offset(offset).limit(limit).all()
            
            return [article.to_dict() for article in articles]
            
        except Exception as e:
            logger.error(f"Error getting news from database: {e}")
            return []
        finally:
            db.close()
    
    def get_featured_news(self, limit: int = 5) -> List[Dict]:
        """Get featured news articles"""
        try:
            db = self.get_db_session()
            
            articles = db.query(News).filter(
                News.is_featured == True,
                News.is_active == True
            ).order_by(desc(News.published_date)).limit(limit).all()
            
            return [article.to_dict() for article in articles]
            
        except Exception as e:
            logger.error(f"Error getting featured news: {e}")
            return []
        finally:
            db.close()
    
    def search_news(self, query: str, limit: int = 20) -> List[Dict]:
        """Search news articles"""
        try:
            db = self.get_db_session()
            
            articles = db.query(News).filter(
                News.is_active == True,
                (News.title.contains(query)) | 
                (News.content.contains(query)) |
                (News.tags.contains(query))
            ).order_by(desc(News.published_date)).limit(limit).all()
            
            return [article.to_dict() for article in articles]
            
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []
        finally:
            db.close()
    
    def increment_read_count(self, news_id: int) -> bool:
        """Increment read count for a news article"""
        try:
            db = self.get_db_session()
            
            news = db.query(News).filter(News.id == news_id).first()
            if news:
                news.read_count += 1
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error incrementing read count: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_news_categories(self) -> List[Dict]:
        """Get all news categories"""
        try:
            db = self.get_db_session()
            
            categories = db.query(NewsCategory).filter(NewsCategory.is_active == True).all()
            
            return [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'description': cat.description,
                    'color': cat.color,
                    'icon': cat.icon
                }
                for cat in categories
            ]
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
        finally:
            db.close()
    
    def subscribe_to_newsletter(self, email: str, categories: List[str] = None) -> bool:
        """Subscribe to newsletter"""
        try:
            db = self.get_db_session()
            
            # Check if already subscribed
            existing = db.query(NewsSubscription).filter(NewsSubscription.email == email).first()
            
            if existing:
                # Update categories if provided
                if categories:
                    existing.categories = ','.join(categories)
                db.commit()
                return True
            
            # Create new subscription
            subscription = NewsSubscription(
                email=email,
                categories=','.join(categories) if categories else ''
            )
            db.add(subscription)
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to newsletter: {e}")
            db.rollback()
            return False
        finally:
            db.close() 