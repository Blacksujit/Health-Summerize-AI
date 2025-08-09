import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import os
from .models import News, NewsCategory, NewsSubscription, init_news_db
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
import re
from textblob import TextBlob
import threading
import time
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Simple in-memory rate limiter for API calls.
    This is per-process and not distributed. For production, use Redis or similar.
    """
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.lock = threading.Lock()
        self.request_times = []

    def allow_request(self) -> bool:
        with self.lock:
            now = time.time()
            self.request_times = [t for t in self.request_times if now - t < self.window_seconds]
            if len(self.request_times) < self.max_requests:
                self.request_times.append(now)
                return True
            return False

    def get_remaining(self) -> int:
        with self.lock:
            now = time.time()
            self.request_times = [t for t in self.request_times if now - t < self.window_seconds]
            return self.max_requests - len(self.request_times)

    def get_reset_time(self) -> float:
        with self.lock:
            now = time.time()
            if not self.request_times:
                return 0
            oldest = min(self.request_times)
            return max(0, self.window_seconds - (now - oldest))

class NewsService:
    RAPIDAPI_REQUEST_LIMIT = 100
    RAPIDAPI_WINDOW_SECONDS = 3600  # 1 hour

    def __init__(self):
        # Load API keys from environment variables
        self.api_keys = {
            'rapidapi': os.environ.get('RAPID_API_KEY', None)
        }
        self.SessionLocal = init_news_db()
        self.rapidapi_rate_limiter = RateLimiter(self.RAPIDAPI_REQUEST_LIMIT, self.RAPIDAPI_WINDOW_SECONDS)

    def get_db_session(self) -> Session:
        return self.SessionLocal()

    def fetch_healthcare_news(self, category: str = 'HEALTH', page_size: int = 10, country: str = 'IN') -> List[Dict]:
        """
        Fetch news using the RapidAPI real-time-news-data API.
        """
        try:
            if not self.rapidapi_rate_limiter.allow_request():
                reset_in = self.rapidapi_rate_limiter.get_reset_time()
                logger.warning(f"RapidAPI rate limit reached. Try again in {int(reset_in)} seconds.")
                return [{
                    "status": "error",
                    "code": "rateLimitExceeded",
                    "message": f"API rate limit reached. Try again in {int(reset_in)} seconds."
                }]

            rapidapi_key = self.api_keys.get('rapidapi')
            if not rapidapi_key:
                logger.error("RapidAPI key is missing. Please set the RAPIDAPI_KEY environment variable.")
                return [{
                    "status": "error",
                    "code": "apiKeyMissing",
                    "message": "Your RapidAPI key is missing. Please set the RAPIDAPI_KEY environment variable."
                }]

            url = "https://real-time-news-data.p.rapidapi.com/topic-news-by-section"
            querystring = {
                "topic": category,
                "section": "CAQiSkNCQVNNUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENJT0NBUWFDZ29JTDIwdk1ETnliSFFxQ2hJSUwyMHZNRE55YkhRb0FBKi4IACoqCAoiJENCQVNGUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENnQVABUAE",
                "limit": str(page_size),
                "country": country,
                "lang": "en"
            }
            headers = {
                "x-rapidapi-key": rapidapi_key,
                "x-rapidapi-host": "real-time-news-data.p.rapidapi.com"
            }

            logger.info(f"Requesting news from RapidAPI: {url} params={querystring}")
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            logger.info(f"RapidAPI response status: {response.status_code}")

            try:
                data = response.json()
                if isinstance(data, dict) and "message" in data and "Invalid API key" in data["message"]:
                    logger.error(f"RapidAPI Invalid API key error: {data['message']}")
                    return [{
                        "status": "error",
                        "code": "invalidApiKey",
                        "message": data["message"]
                    }]
            except Exception:
                pass

            if response.status_code != 200:
                logger.error(f"RapidAPI returned non-200 status: {response.status_code} {response.text}")
            response.raise_for_status()
            data = response.json()
            logger.debug(f"RapidAPI response data: {json.dumps(data)[:500]}")
            articles = data.get('data', [])
            if not articles:
                logger.warning("No articles found in RapidAPI response. Full response: %s", data)
            processed_articles = []
            for article in articles:
                processed_article = self._process_rapidapi_article(article)
                if processed_article:
                    processed_articles.append(processed_article)
            return processed_articles
        except Exception as e:
            logger.error(f"Error fetching news from RapidAPI: {e}", exc_info=True)
            return self._get_mock_news()

    def _process_rapidapi_article(self, article: Dict) -> Optional[Dict]:
        try:
            title = article.get('title', '').strip()
            content = article.get('content', '') or article.get('description', '')
            if content:
                content = re.sub(r'\[.*?\]', '', content)
                content = re.sub(r'\(.*?\)', '', content)
                content = content.strip()
            summary = self._generate_summary(content) if content else None
            sentiment_score = self._analyze_sentiment(content) if content else None
            # Handle source as dict or string
            source = article.get('source', '')
            if isinstance(source, dict):
                source = source.get('name', 'Unknown')
            if not source:
                source = 'Unknown'
            url = article.get('url', '')
            image_url = article.get('image_url', '') or article.get('image', '') or article.get('urlToImage', '')
            published_date = article.get('published_datetime', '') or article.get('publishedAt', '')
            # Convert published_date to datetime object if possible
            published_date_dt = None
            if published_date:
                try:
                    published_date_dt = date_parser.parse(published_date)
                except Exception:
                    published_date_dt = None
            tags = self._extract_tags(f"{title} {content}")
            return {
                'title': title,
                'content': content,
                'summary': summary,
                'source': source,
                'url': url,
                'image_url': image_url,
                'category': 'HEALTH',
                'tags': tags,
                'published_date': published_date_dt,
                'sentiment_score': sentiment_score,
                'ai_generated': False
            }
        except Exception as e:
            logger.error(f"Error processing RapidAPI article: {e}")
            return None

    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        try:
            if len(content) <= max_length:
                return content
            sentences = content.split('.')
            summary = '. '.join(sentences[:2]) + '.'
            if len(summary) > max_length:
                summary = summary[:max_length-3] + '...'
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return content[:max_length] + '...' if len(content) > max_length else content

    def _analyze_sentiment(self, text: str) -> Optional[float]:
        try:
            if not text:
                return None
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return None

    def _extract_tags(self, text: str) -> List[str]:
        try:
            keywords = [
                'health', 'healthcare', 'medicine', 'medical', 'doctor', 'physician', 'nurse', 'patient', 'diagnosis', 'treatment', 'therapy', 'hospital', 'clinic', 'telemedicine', 'telehealth', 'ehr', 'emr', 'electronic health record', 'summarization', 'virtual consultation', 'appointment', 'consultation', 'ai', 'artificial intelligence', 'machine learning', 'deep learning', 'nlp', 'natural language processing', 'medisync', 'imaging', 'x-ray', 'radiology', 'ct', 'mri', 'ultrasound', 'scan', 'pharmacy', 'drug', 'medication', 'prescription', 'wellness', 'mental health', 'psychology', 'psychiatry', 'cardiology', 'oncology', 'pediatrics', 'geriatrics', 'innovation', 'technology', 'data', 'cloud', 'cybersecurity', 'privacy', 'security', 'mobile', 'software', 'hardware', 'internet', 'research', 'biotech', 'genomics', 'public health', 'insurance', 'compliance', 'hipaa', 'report', 'analysis', 'analytics', 'monitoring', 'wearable', 'device', 'remote monitoring', 'triage', 'screening', 'prevention', 'chronic disease', 'diabetes', 'cancer', 'covid', 'infection', 'emergency', 'surgery', 'lab', 'test', 'blood', 'vitals', 'record', 'care', 'support', 'access', 'outcome', 'quality', 'safety'
            ]
            text_lower = text.lower()
            found_tags = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_tags.append(keyword.title())
            return found_tags[:5]
        except Exception as e:
            logger.error(f"Error extracting tags: {e}")
            return []

    def _get_mock_news(self) -> List[Dict]:
        return [
            {
                'title': 'AI Revolutionizes Technology Sector',
                'content': 'Artificial Intelligence is transforming the technology industry with new innovations and smarter solutions.',
                'summary': 'AI is driving major changes in technology.',
                'source': 'Tech News',
                'url': '#',
                'image_url': '/static/images/news-img.png',
                'category': 'HEALTH',
                'tags': ['Healthcare', 'Telemedicine', 'AI', 'Technology', 'Innovation'],
                'published_date': datetime.now(),
                'sentiment_score': 0.5,
                'ai_generated': False
            }
        ]

    def save_news_to_db(self, news_data: List[Dict]) -> bool:
        db = self.get_db_session()
        try:
            for article_data in news_data:
                existing = db.query(News).filter(
                    News.title == article_data['title'],
                    News.source == article_data['source']
                ).first()
                if not existing:
                    # Ensure tags are stored as comma-separated string if needed
                    if isinstance(article_data.get('tags'), list):
                        article_data['tags'] = ','.join(article_data['tags'])
                    # Ensure published_date is a datetime object or None
                    published_date = article_data.get('published_date')
                    if published_date:
                        if isinstance(published_date, str):
                            try:
                                article_data['published_date'] = date_parser.parse(published_date)
                            except Exception:
                                article_data['published_date'] = None
                        elif not isinstance(published_date, (datetime, )):
                            article_data['published_date'] = None
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
        db = self.get_db_session()
        try:
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
        db = self.get_db_session()
        try:
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
        """
        More robust search logic to get specific articles related to the search query.
        - Matches whole words (case-insensitive)
        - Ranks articles by relevance (number of matches in title, content, tags)
        - Filters out articles that are not closely related to the query
        """
        db = self.get_db_session()
        try:
            # Preprocess query for robust matching
            query = query.strip()
            if not query:
                return []

            # Split query into keywords (support multi-word queries)
            keywords = [kw.lower() for kw in re.findall(r'\w+', query)]
            if not keywords:
                return []

            # Build SQLAlchemy filters for each keyword (whole word, case-insensitive)
            filters = []
            for kw in keywords:
                # Use ilike for case-insensitive matching
                filters.append(or_(
                    News.title.ilike(f'%{kw}%'),
                    News.content.ilike(f'%{kw}%'),
                    News.tags.ilike(f'%{kw}%')
                ))

            # Only fetch a larger pool, then filter and rank in Python for best matches
            candidate_articles = db.query(News).filter(
                News.is_active == True,
                and_(*filters)
            ).order_by(desc(News.published_date)).limit(100).all()

            # Rank and filter articles by relevance
            def relevance_score(article):
                score = 0
                title = (article.title or "").lower()
                content = (article.content or "").lower()
                tags = (article.tags or "").lower()
                for kw in keywords:
                    # Whole word match in title
                    if re.search(r'\b' + re.escape(kw) + r'\b', title):
                        score += 5
                    # Whole word match in tags
                    if re.search(r'\b' + re.escape(kw) + r'\b', tags):
                        score += 4
                    # Whole word match in content
                    if re.search(r'\b' + re.escape(kw) + r'\b', content):
                        score += 2
                    # Partial match fallback (less weight)
                    if kw in title:
                        score += 2
                    if kw in tags:
                        score += 1
                    if kw in content:
                        score += 1
                return score

            # Filter out articles with zero score (not really related)
            scored_articles = [
                (article, relevance_score(article))
                for article in candidate_articles
            ]
            # Only keep articles with a positive score
            scored_articles = [item for item in scored_articles if item[1] > 0]

            # Sort by score (desc), then by published_date
            scored_articles.sort(key=lambda x: (x[1], x[0].published_date), reverse=True)

            # Return up to 'limit' articles
            return [article.to_dict() for article, _ in scored_articles[:limit]]

        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []
        finally:
            db.close()

    def increment_read_count(self, news_id: int) -> bool:
        db = self.get_db_session()
        try:
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
        db = self.get_db_session()
        try:
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
        db = self.get_db_session()
        try:
            existing = db.query(NewsSubscription).filter(NewsSubscription.email == email).first()
            if existing:
                if categories:
                    existing.categories = ','.join(categories)
                db.commit()
                return True
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