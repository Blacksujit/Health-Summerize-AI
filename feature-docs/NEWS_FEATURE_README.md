# Medivance News Feature

## Overview

The Medivance News Feature is a comprehensive healthcare news system that provides AI-powered news curation, real-time updates, and intelligent content management. This feature helps users stay informed about the latest developments in healthcare, medical research, and AI innovations.

## Features

### 🎯 Core Features

1. **AI-Powered News Curation**
   - Automatic news fetching from multiple sources
   - AI-driven content summarization
   - Sentiment analysis for news articles
   - Intelligent tag extraction

2. **Dynamic News Management**
   - Real-time news updates
   - Category-based filtering
   - Advanced search functionality
   - Pagination support

3. **User Experience**
   - Modern, responsive design
   - Interactive news cards
   - Newsletter subscription
   - Related articles suggestions

4. **Admin Features**
   - News article management
   - Category management
   - Newsletter management
   - Analytics and insights

### 🚀 Innovative Features

1. **AI Sentiment Analysis**
   - Automatic sentiment scoring for articles
   - Visual sentiment indicators
   - Emotion-based content filtering

2. **Smart Content Recommendations**
   - AI-powered related articles
   - Personalized content suggestions
   - Reading history tracking

3. **Real-time Updates**
   - Live news refresh
   - Push notifications (future)
   - RSS feed integration

4. **Advanced Search**
   - Full-text search
   - Category-based filtering
   - Tag-based search
   - Date range filtering

## Technical Implementation

### Database Schema

```sql
-- News Articles Table
CREATE TABLE news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    source VARCHAR(200),
    url VARCHAR(500),
    image_url VARCHAR(500),
    category VARCHAR(100),
    tags VARCHAR(500),
    published_date DATETIME,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    sentiment_score FLOAT,
    read_count INTEGER DEFAULT 0,
    ai_generated BOOLEAN DEFAULT FALSE
);

-- News Categories Table
CREATE TABLE news_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7),
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Newsletter Subscriptions Table
CREATE TABLE news_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(200) NOT NULL UNIQUE,
    categories VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_sent DATETIME
);
```

### API Endpoints

#### News Management
- `GET /news` - Main news page with filtering
- `GET /news/<int:news_id>` - News article detail
- `GET /api/news` - News articles API
- `GET /api/news/featured` - Featured news API
- `GET /api/news/categories` - News categories API
- `GET /api/news/search` - News search API
- `POST /api/news/subscribe` - Newsletter subscription
- `POST /api/news/fetch` - Fetch fresh news
- `POST /news/refresh` - Refresh news manually

#### Category Management
- `GET /news/category/<category>` - News by category
- `GET /news/search` - News search page

### File Structure

```
app/
├── models.py                 # Database models
├── news_service.py          # News service logic
├── routes.py               # News routes
└── __init__.py             # App initialization

templates/
├── news.html              # Main news page
└── news_detail.html       # News article detail

database/
└── news.db               # News database
```

## Installation & Setup

### Prerequisites

1. Python 3.8+
2. Flask framework
3. SQLAlchemy
4. Required Python packages (see requirements.txt)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-Health-Summerize
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Add your API keys
   NEWS_API_KEY=your_news_api_key
   OPENAI_API_KEY=your_openai_api_key
   RAPIDAPI_KEY=your_rapidapi_key
   ```

4. **Initialize the database**
   ```bash
   python -c "from app.models import init_news_db; init_news_db()"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Configuration

### Environment Variables

```env
# News API Configuration
NEWS_API_KEY=your_news_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here

# AI Services
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///database/news.db

# Cache Configuration
CACHE_TYPE=filesystem
CACHE_DIR=./cache
```

### API Keys Setup

1. **NewsAPI** (https://newsapi.org/)
   - Sign up for free API key
   - Add to environment variables

2. **OpenAI** (https://openai.com/)
   - Get API key from OpenAI dashboard
   - Add to environment variables

3. **RapidAPI** (https://rapidapi.com/)
   - Sign up for additional news APIs
   - Add to environment variables

## Usage

### For Users

1. **Browse News**
   - Visit `/news` to see all news articles
   - Use category filters to find specific topics
   - Search for specific keywords

2. **Read Articles**
   - Click on any news card to read full article
   - View related articles at the bottom
   - Check sentiment analysis indicators

3. **Subscribe to Newsletter**
   - Enter email in newsletter section
   - Choose preferred categories
   - Receive regular updates

### For Administrators

1. **Manage News**
   - Access news management panel
   - Add/edit/delete articles
   - Manage categories

2. **Monitor Analytics**
   - View read counts
   - Track popular articles
   - Monitor user engagement

3. **Content Curation**
   - Feature important articles
   - Manage AI-generated content
   - Control content quality

## Customization

### Adding New Categories

1. **Database Method**
   ```python
   from app.models import NewsCategory, init_news_db
   from sqlalchemy.orm import sessionmaker
   
   SessionLocal = init_news_db()
   db = SessionLocal()
   
   new_category = NewsCategory(
       name="Mental Health",
       description="Mental health and wellness news",
       color="#FF6B6B",
       icon="fa fa-brain"
   )
   db.add(new_category)
   db.commit()
   ```

2. **API Method**
   ```bash
   curl -X POST /api/news/categories \
   -H "Content-Type: application/json" \
   -d '{"name": "Mental Health", "description": "Mental health news"}'
   ```

### Customizing News Sources

Edit `app/news_service.py` to add new news sources:

```python
def fetch_custom_news(self):
    """Fetch news from custom source"""
    # Add your custom news fetching logic here
    pass
```

### Styling Customization

Modify CSS in `templates/news.html`:

```css
/* Custom news card styling */
.news-card {
    /* Your custom styles */
}
```

## Troubleshooting

### Common Issues

1. **News API Not Working**
   - Check API key in environment variables
   - Verify API quota limits
   - Check network connectivity

2. **Database Errors**
   - Ensure database file exists
   - Check file permissions
   - Verify SQLAlchemy installation

3. **Search Not Working**
   - Check database indexes
   - Verify search implementation
   - Test with simple queries

### Debug Mode

Enable debug mode for detailed error messages:

```python
app.run(debug=True, port=600)
```

## Future Enhancements

### Planned Features

1. **AI-Powered Recommendations**
   - Machine learning-based content suggestions
   - User behavior analysis
   - Personalized news feeds

2. **Advanced Analytics**
   - User engagement metrics
   - Content performance tracking
   - A/B testing capabilities

3. **Social Features**
   - User comments and ratings
   - Social sharing integration
   - Community discussions

4. **Mobile App**
   - Native mobile application
   - Push notifications
   - Offline reading

5. **Multilingual Support**
   - Multiple language support
   - Automatic translation
   - Localized content

### Technical Improvements

1. **Performance Optimization**
   - Caching strategies
   - Database optimization
   - CDN integration

2. **Scalability**
   - Microservices architecture
   - Load balancing
   - Auto-scaling

3. **Security**
   - Content moderation
   - User authentication
   - Data encryption

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Email: nirmalsujit981@gmail.com
- support: refer Project Readme file

## Acknowledgments

- NewsAPI for news data
- OpenAI for AI services
- Flask community for framework
- Contributors and maintainers 