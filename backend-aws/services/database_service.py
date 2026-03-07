"""Lambda-compatible Aurora PostgreSQL database service using psycopg2"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from datetime import datetime

# Database configuration from environment variables
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'hiveminddb')
DB_USER = os.getenv('DB_USER', 'hivemind')
DB_PASSWORD = os.getenv('DB_PASSWORD')


def get_db_connection():
    """
    Create database connection using environment variables.
    Connection must be closed by caller.
    """
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=5
    )


@contextmanager
def db_connection():
    """
    Context manager for database connections.
    Automatically closes connection after use.
    
    Usage:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM brands")
    """
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ==================== Brand Operations ====================

def create_brand(brand_id: str, name: str, industry: str) -> Dict[str, Any]:
    """Create brand in Aurora"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO brands (id, name, industry, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, industry, created_at
            """,
            (brand_id, name, industry, datetime.utcnow())
        )
        result = cursor.fetchone()
        return dict(result)


def get_brand(brand_id: str) -> Optional[Dict[str, Any]]:
    """Get brand from Aurora"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM brands WHERE id = %s",
            (brand_id,)
        )
        result = cursor.fetchone()
        return dict(result) if result else None


def list_brands(limit: int = 100) -> List[Dict[str, Any]]:
    """List all brands"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM brands ORDER BY created_at DESC LIMIT %s",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


# ==================== Social Post Operations ====================

def create_post(
    post_id: str,
    brand_id: str,
    platform: str,
    content: str,
    media_url: Optional[str] = None
) -> Dict[str, Any]:
    """Create social post in Aurora"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO social_posts (id, brand_id, platform, content, media_url, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, brand_id, platform, content, media_url, status, created_at
            """,
            (post_id, brand_id, platform, content, media_url, datetime.utcnow())
        )
        result = cursor.fetchone()
        return dict(result)


def get_post(post_id: str) -> Optional[Dict[str, Any]]:
    """Get social post from Aurora"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM social_posts WHERE id = %s",
            (post_id,)
        )
        result = cursor.fetchone()
        return dict(result) if result else None


def get_brand_posts(brand_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get posts for a brand"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT * FROM social_posts
            WHERE brand_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (brand_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


def update_post_status(post_id: str, status: str) -> bool:
    """Update post status (draft, published, archived)"""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE social_posts SET status = %s WHERE id = %s",
            (status, post_id)
        )
        return cursor.rowcount > 0


# ==================== Engagement Operations ====================

def track_engagement(
    post_id: str,
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    clicks: int = 0
) -> Dict[str, Any]:
    """Track or update engagement metrics"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Upsert engagement data
        cursor.execute(
            """
            INSERT INTO engagement (id, post_id, likes, comments, shares, clicks, updated_at)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s)
            ON CONFLICT (post_id) DO UPDATE SET
                likes = EXCLUDED.likes,
                comments = EXCLUDED.comments,
                shares = EXCLUDED.shares,
                clicks = EXCLUDED.clicks,
                updated_at = EXCLUDED.updated_at
            RETURNING id, post_id, likes, comments, shares, clicks, updated_at
            """,
            (post_id, likes, comments, shares, clicks, datetime.utcnow())
        )
        result = cursor.fetchone()
        return dict(result)


def get_post_analytics(post_id: str) -> Dict[str, Any]:
    """Get post with engagement analytics"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT p.*, e.likes, e.comments, e.shares, e.clicks
            FROM social_posts p
            LEFT JOIN engagement e ON p.id = e.post_id
            WHERE p.id = %s
            """,
            (post_id,)
        )
        result = cursor.fetchone()
        return dict(result) if result else {}


# ==================== Video Operations ====================

def store_video_metadata(
    video_id: str,
    s3_url: str,
    duration: float,
    transcription: Optional[str] = None
) -> Dict[str, Any]:
    """Store video metadata in Aurora"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO videos (id, s3_url, duration, transcription, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, s3_url, duration, transcription, status, created_at
            """,
            (video_id, s3_url, duration, transcription, datetime.utcnow())
        )
        result = cursor.fetchone()
        return dict(result)


def update_video_transcription(video_id: str, transcription: str) -> bool:
    """Update video transcription after processing"""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE videos
            SET transcription = %s, status = 'completed', processed_at = %s
            WHERE id = %s
            """,
            (transcription, datetime.utcnow(), video_id)
        )
        return cursor.rowcount > 0


def get_video(video_id: str) -> Optional[Dict[str, Any]]:
    """Get video metadata"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM videos WHERE id = %s",
            (video_id,)
        )
        result = cursor.fetchone()
        return dict(result) if result else None


# ==================== Article Operations ====================

def create_article(
    article_id: str,
    title: str,
    url: str,
    category: str,
    published_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create article in Aurora"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO articles (id, title, url, category, published_date, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, title, url, category, published_date, created_at
            """,
            (article_id, title, url, category, published_date, datetime.utcnow())
        )
        result = cursor.fetchone()
        return dict(result)


def get_articles_by_category(category: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get articles by category"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT * FROM articles
            WHERE category = %s
            ORDER BY published_date DESC
            LIMIT %s
            """,
            (category, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


# ==================== User Preferences ====================

def get_user_preferences(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user preferences"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM user_preferences WHERE user_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        return dict(result) if result else None


def upsert_user_preferences(
    user_id: str,
    preferred_platforms: List[str],
    preferred_categories: List[str],
    notification_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """Create or update user preferences"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO user_preferences (user_id, preferred_platforms, preferred_categories, notification_settings, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                preferred_platforms = EXCLUDED.preferred_platforms,
                preferred_categories = EXCLUDED.preferred_categories,
                notification_settings = EXCLUDED.notification_settings,
                updated_at = EXCLUDED.updated_at
            RETURNING user_id, preferred_platforms, preferred_categories, notification_settings, updated_at
            """,
            (user_id, preferred_platforms, preferred_categories, notification_settings, datetime.utcnow(), datetime.utcnow())
        )
        result = cursor.fetchone()
        return dict(result)


# ==================== Analytics ====================

def store_performance_analytics(
    brand_id: str,
    platform: str,
    date: datetime,
    total_posts: int,
    total_engagement: int,
    avg_engagement_rate: float
) -> Dict[str, Any]:
    """Store daily performance analytics"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO performance_analytics (id, brand_id, platform, date, total_posts, total_engagement, avg_engagement_rate, created_at)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, brand_id, platform, date, total_posts, total_engagement, avg_engagement_rate
            """,
            (brand_id, platform, date, total_posts, total_engagement, avg_engagement_rate, datetime.utcnow())
        )
        result = cursor.fetchone()
        return dict(result)


def get_brand_analytics(brand_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """Get brand analytics for last N days"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT * FROM performance_analytics
            WHERE brand_id = %s AND date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY date DESC
            """,
            (brand_id, days)
        )
        return [dict(row) for row in cursor.fetchall()]
