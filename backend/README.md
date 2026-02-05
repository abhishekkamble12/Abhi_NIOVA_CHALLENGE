# 🏎️ Racing Demo Backend

High-performance FastAPI backend for the motorsport-inspired frontend demo. Built with modern Python async patterns, comprehensive caching, real-time capabilities, and production-ready architecture.

## ✨ Features

- **🚀 FastAPI Framework**: Modern, fast, and async Python web framework
- **🗄️ PostgreSQL Database**: Robust relational database with async SQLAlchemy
- **⚡ Redis Caching**: High-performance caching and session storage
- **🔌 WebSocket Support**: Real-time data streaming for live metrics
- **🔐 JWT Authentication**: Secure user authentication and authorization
- **📊 Analytics Tracking**: Comprehensive user behavior and performance analytics
- **🎯 RESTful APIs**: Well-structured API endpoints with OpenAPI documentation
- **🔄 Background Tasks**: Async task processing with Celery-style patterns
- **📈 Performance Monitoring**: Built-in metrics and health checks
- **🛡️ Security**: CORS, rate limiting, and input validation

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLAlchemy 2.0 (async)
- **Cache**: Redis
- **Authentication**: JWT with passlib
- **Validation**: Pydantic v2
- **WebSockets**: Native FastAPI WebSocket support
- **Testing**: Pytest with async support

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+

### Installation

1. **Clone and navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis credentials
   ```

5. **Run the development server**:
   ```bash
   python run.py
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                    # API routes
│   │   └── v1/
│   │       ├── endpoints/      # Individual endpoint modules
│   │       └── api.py         # Route aggregation
│   ├── core/                  # Core functionality
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database connection
│   │   ├── redis.py          # Redis client
│   │   └── websocket.py      # WebSocket handlers
│   ├── models/               # SQLAlchemy models
│   │   ├── user.py          # User model
│   │   ├── race.py          # Racing data models
│   │   ├── helmet.py        # Helmet collection models
│   │   ├── performance.py   # Performance metrics
│   │   ├── content.py       # Content management
│   │   └── analytics.py     # Analytics models
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py         # User schemas
│   │   ├── race.py         # Racing schemas
│   │   └── ...             # Other schemas
│   └── main.py             # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── run.py                # Development server script
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/racing_demo

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Database Setup

1. **Create PostgreSQL database**:
   ```sql
   CREATE DATABASE racing_demo;
   CREATE USER racing_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE racing_demo TO racing_user;
   ```

2. **Tables are created automatically** when the application starts.

## 📚 API Documentation

### Core Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/refresh` - Refresh access token

#### Racing Data
- `GET /api/v1/races/` - Get races with filtering
- `GET /api/v1/races/current-season` - Get current season races
- `GET /api/v1/races/recent-results` - Get recent race results
- `GET /api/v1/races/statistics` - Get racing statistics
- `GET /api/v1/races/{race_id}` - Get specific race
- `GET /api/v1/races/{race_id}/results` - Get race results

#### Helmet Collection
- `GET /api/v1/helmets/` - Get helmets with filtering
- `GET /api/v1/helmets/featured` - Get featured helmets
- `GET /api/v1/helmets/seasons` - Get available seasons
- `GET /api/v1/helmets/stats` - Get collection statistics
- `GET /api/v1/helmets/{helmet_id}` - Get specific helmet
- `GET /api/v1/helmets/{helmet_id}/designs` - Get helmet designs

#### Performance Metrics
- `GET /api/v1/performance/web-vitals` - Get Core Web Vitals
- `GET /api/v1/performance/lighthouse` - Get Lighthouse scores
- `GET /api/v1/performance/summary` - Get performance summary
- `GET /api/v1/performance/real-time` - Get real-time metrics
- `GET /api/v1/performance/uptime` - Get uptime statistics

#### Content Management
- `GET /api/v1/content/` - Get content with filtering
- `GET /api/v1/content/featured` - Get featured content
- `GET /api/v1/content/campaigns/` - Get campaigns
- `GET /api/v1/content/social-posts/` - Get social posts
- `GET /api/v1/content/social-posts/stats` - Get social media stats

#### Analytics
- `POST /api/v1/analytics/events` - Track analytics event
- `GET /api/v1/analytics/summary` - Get analytics summary
- `GET /api/v1/analytics/real-time` - Get real-time analytics
- `GET /api/v1/analytics/funnel` - Get conversion funnel

#### Dashboard
- `GET /api/v1/dashboard/overview` - Get dashboard overview
- `GET /api/v1/dashboard/live-stats` - Get live statistics
- `GET /api/v1/dashboard/performance-summary` - Get performance summary
- `GET /api/v1/dashboard/analytics-summary` - Get analytics summary

### WebSocket Endpoints

- `ws://localhost:8000/ws/live-data` - Real-time racing data
- `ws://localhost:8000/ws/performance-metrics` - Performance metrics stream
- `ws://localhost:8000/ws/notifications` - System notifications

## 🔄 Real-time Features

### WebSocket Connections

The backend provides real-time data streaming through WebSocket connections:

```javascript
// Connect to live racing data
const ws = new WebSocket('ws://localhost:8000/ws/live-data');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Live racing data:', data);
};
```

### Live Data Types

- **Racing Telemetry**: Speed, lap times, position, tire temperature
- **Performance Metrics**: Response times, active users, system health
- **System Notifications**: Updates, alerts, status changes

## 📊 Caching Strategy

### Redis Caching

The backend implements comprehensive caching:

- **API Responses**: Frequently accessed data cached for 5-30 minutes
- **Database Queries**: Complex queries cached to reduce load
- **Session Data**: User sessions and authentication tokens
- **Real-time Counters**: Analytics and performance counters

### Cache Keys

```python
# Examples of cache keys used
"helmets:featured"              # Featured helmets (10 min)
"races:statistics"              # Racing statistics (1 hour)
"performance:web_vitals"        # Web vitals (5 min)
"dashboard:overview"            # Dashboard data (5 min)
"analytics:summary:30"          # 30-day analytics (15 min)
```

## 🛡️ Security Features

### Authentication & Authorization

- **JWT Tokens**: Secure stateless authentication
- **Password Hashing**: bcrypt for secure password storage
- **Token Expiration**: Configurable token lifetime
- **Refresh Tokens**: Secure token renewal

### API Security

- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **Rate Limiting**: Built-in request rate limiting

## 📈 Performance Optimization

### Database Optimization

- **Connection Pooling**: Efficient database connections
- **Async Queries**: Non-blocking database operations
- **Indexing**: Optimized database indexes
- **Query Optimization**: Efficient SQLAlchemy queries

### Caching & Performance

- **Redis Caching**: High-performance in-memory caching
- **Response Compression**: GZip compression middleware
- **Static File Serving**: Efficient static file handling
- **Background Tasks**: Async task processing

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Test Structure

```
tests/
├── test_auth.py           # Authentication tests
├── test_races.py          # Racing API tests
├── test_helmets.py        # Helmet API tests
├── test_performance.py    # Performance API tests
└── conftest.py           # Test configuration
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**:
   ```env
   ENVIRONMENT=production
   DEBUG=false
   DATABASE_URL=postgresql://user:pass@prod-db:5432/racing_demo
   REDIS_URL=redis://prod-redis:6379/0
   ```

2. **Database Migration**:
   ```bash
   # Tables are created automatically on startup
   # For production, consider using Alembic for migrations
   ```

3. **Run with Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Checks

The API provides health check endpoints:

- `GET /health` - Basic health check
- `GET /` - API status and version info

## 📝 API Examples

### Authentication

```bash
# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "driver@racing.com",
    "username": "racing_driver",
    "password": "secure_password"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=racing_driver&password=secure_password"
```

### Get Racing Statistics

```bash
curl "http://localhost:8000/api/v1/races/statistics"
```

### Get Performance Metrics

```bash
curl "http://localhost:8000/api/v1/performance/summary"
```

### Track Analytics Event

```bash
curl -X POST "http://localhost:8000/api/v1/analytics/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "page_view",
    "event_type": "page_view",
    "session_id": "session_123",
    "page_url": "/helmets",
    "event_timestamp": "2026-01-31T12:00:00Z"
  }'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

MIT License - feel free to use this project for your own purposes.

---

**Built with ⚡ FastAPI and designed for high-performance racing applications.**