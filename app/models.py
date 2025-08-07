from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

Base = declarative_base()

class News(Base):
    __tablename__ = 'news'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    source = Column(String(200))
    url = Column(String(500))
    image_url = Column(String(500))
    category = Column(String(100))
    tags = Column(String(500))  # Comma-separated tags
    published_date = Column(DateTime, default=datetime.utcnow)
    created_date = Column(DateTime, default=datetime.utcnow)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sentiment_score = Column(Float)  # AI sentiment analysis score
    read_count = Column(Integer, default=0)
    ai_generated = Column(Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'source': self.source,
            'url': self.url,
            'image_url': self.image_url,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'is_featured': self.is_featured,
            'is_active': self.is_active,
            'sentiment_score': self.sentiment_score,
            'read_count': self.read_count,
            'ai_generated': self.ai_generated
        }

class NewsCategory(Base):
    __tablename__ = 'news_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    icon = Column(String(50))  # FontAwesome icon class
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class NewsSubscription(Base):
    __tablename__ = 'news_subscriptions'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(200), nullable=False, unique=True)
    categories = Column(String(500))  # Comma-separated category IDs
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_sent = Column(DateTime)

# Database setup
def init_news_db():
    """Initialize the news database"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'news.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal

def get_news_db():
    """Get database session"""
    SessionLocal = init_news_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 