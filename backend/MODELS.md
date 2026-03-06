# Database Models Documentation

## Overview

Complete SQLAlchemy models for AI Media OS platform with vector embeddings, relationships, and AI-powered features.

## Models

### 1. User
**Purpose**: Authentication and user management

**Fields**:
- `id` (UUID) - Primary key
- `email` (String) - Unique email address
- `username` (String) - Unique username
- `password_hash` (String) - Hashed password
- `full_name` (String) - User's full name
- `is_active` (Boolean) - Account status
- `is_verified` (Boolean) - Email verification status
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

**Relationships**:
- `brands` → One-to-many with Brand
- `generated_posts` → One-to-many with GeneratedPost
- `preferences` → One-to-one with UserPreferences
- `behaviors` → One-to-many with UserBehavior

---

### 2. Brand
**Purpose**: Brand identity and voice management

**Fields**:
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to User
- `name` (String) - Brand name
- `description` (Text) - Brand description
- `industry` (String) - Industry category
- `tone` (String) - Brand tone (professional, casual, etc.)
- `target_audience` (Text) - Target audience description
- `brand_voice` (Text) - Brand voice guidelines
- `embedding` (Vector) - **384-dim vector for brand identity**
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships**:
- `user` → Many-to-one with User
- `generated_posts` → One-to-many with GeneratedPost

**Vector Use Case**: Semantic search for similar brands, brand matching

---

### 3. GeneratedPost
**Purpose**: AI-generated social media posts

**Fields**:
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to User
- `brand_id` (UUID) - Foreign key to Brand
- `platform` (Enum) - instagram, linkedin, twitter, facebook
- `status` (Enum) - draft, scheduled, published, archived
- `content` (Text) - Post content
- `hashtags` (Text) - Hashtags
- `likes` (Integer) - Like count
- `comments` (Integer) - Comment count
- `shares` (Integer) - Share count
- `engagement_rate` (Float) - Engagement percentage
- `ai_model` (String) - AI model used
- `prompt_used` (Text) - Prompt used for generation
- `embedding` (Vector) - **384-dim vector for content similarity**
- `scheduled_at` (DateTime)
- `published_at` (DateTime)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships**:
- `user` → Many-to-one with User
- `brand` → Many-to-one with Brand

**Vector Use Case**: Find similar posts, content recommendations, performance prediction

---

### 4. Article
**Purpose**: News articles for personalized feed

**Fields**:
- `id` (UUID) - Primary key
- `title` (String) - Article title
- `content` (Text) - Article content
- `summary` (Text) - Article summary
- `url` (String) - Unique article URL
- `source` (String) - News source
- `author` (String) - Article author
- `category` (String) - Article category
- `tags` (Array[String]) - Article tags
- `views` (Integer) - View count
- `clicks` (Integer) - Click count
- `relevance_score` (Float) - Relevance score
- `embedding` (Vector) - **384-dim vector for semantic search**
- `published_at` (DateTime)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships**:
- `behaviors` → One-to-many with UserBehavior

**Vector Use Case**: Semantic article search, personalized recommendations, similar articles

---

### 5. Video
**Purpose**: Video content management with AI analysis

**Fields**:
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to User
- `title` (String) - Video title
- `description` (Text) - Video description
- `file_path` (String) - File storage path
- `file_size` (Integer) - File size in bytes
- `duration` (Float) - Duration in seconds
- `resolution` (String) - Video resolution (e.g., "1920x1080")
- `fps` (Integer) - Frames per second
- `codec` (String) - Video codec
- `status` (Enum) - uploading, processing, ready, failed
- `transcript` (Text) - Video transcript
- `summary` (Text) - AI-generated summary
- `embedding` (Vector) - **384-dim vector for video content**
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships**:
- `user` → Many-to-one with User
- `scenes` → One-to-many with VideoScene
- `captions` → One-to-many with Caption

**Vector Use Case**: Video similarity search, content recommendations

---

### 6. VideoScene
**Purpose**: Video scene detection and analysis

**Fields**:
- `id` (UUID) - Primary key
- `video_id` (UUID) - Foreign key to Video
- `start_time` (Float) - Start time in seconds
- `end_time` (Float) - End time in seconds
- `description` (Text) - Scene description
- `scene_type` (String) - action, dialogue, transition, etc.
- `objects_detected` (Text) - JSON string of detected objects
- `suggested_cut` (String) - keep, remove, trim
- `confidence_score` (Float) - AI confidence score
- `embedding` (Vector) - **384-dim vector for scene similarity**
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships**:
- `video` → Many-to-one with Video

**Vector Use Case**: Find similar scenes, scene recommendations, automated editing

---

### 7. Caption
**Purpose**: Video captions and subtitles

**Fields**:
- `id` (UUID) - Primary key
- `video_id` (UUID) - Foreign key to Video
- `start_time` (Float) - Start time in seconds
- `end_time` (Float) - End time in seconds
- `text` (Text) - Caption text
- `language` (String) - Language code (e.g., "en")
- `speaker` (String) - Speaker identification
- `confidence` (Float) - Transcription confidence
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships**:
- `video` → Many-to-one with Video

**Vector Use Case**: None (text-based search sufficient)

---

### 8. UserPreferences
**Purpose**: User preferences for personalization

**Fields**:
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to User (unique)
- `preferred_categories` (Array[String]) - Preferred content categories
- `preferred_sources` (Array[String]) - Preferred news sources
- `blocked_sources` (Array[String]) - Blocked sources
- `preferred_platforms` (Array[String]) - Preferred social platforms
- `content_tone` (String) - Preferred content tone
- `content_length` (String) - Preferred content length
- `email_notifications` (Boolean) - Email notification preference
- `push_notifications` (Boolean) - Push notification preference
- `feed_refresh_interval` (Integer) - Feed refresh interval in minutes
- `embedding` (Vector) - **384-dim vector for preference-based recommendations**
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships**:
- `user` → One-to-one with User

**Vector Use Case**: User similarity, collaborative filtering, personalized recommendations

---

### 9. UserBehavior
**Purpose**: User interaction tracking for AI recommendations

**Fields**:
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to User
- `article_id` (UUID) - Foreign key to Article
- `action_type` (Enum) - view, click, like, share, save, dismiss
- `time_spent` (Integer) - Time spent in seconds
- `scroll_depth` (Float) - Scroll depth percentage
- `device` (String) - Device type
- `platform` (String) - Platform used
- `referrer` (String) - Referrer URL
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships**:
- `user` → Many-to-one with User
- `article` → Many-to-one with Article

**Vector Use Case**: Behavior pattern analysis, recommendation engine training

---

## Relationships Diagram

```
User
├── brands (1:N) → Brand
│   └── generated_posts (1:N) → GeneratedPost
├── generated_posts (1:N) → GeneratedPost
├── preferences (1:1) → UserPreferences
└── behaviors (1:N) → UserBehavior
    └── article (N:1) → Article

Video
├── scenes (1:N) → VideoScene
└── captions (1:N) → Caption
```

## Vector Embeddings Summary

| Model | Vector Field | Dimension | Use Case |
|-------|--------------|-----------|----------|
| Brand | `embedding` | 384 | Brand similarity, matching |
| GeneratedPost | `embedding` | 384 | Content similarity, recommendations |
| Article | `embedding` | 384 | Semantic search, recommendations |
| Video | `embedding` | 384 | Video similarity, recommendations |
| VideoScene | `embedding` | 384 | Scene similarity, automated editing |
| UserPreferences | `embedding` | 384 | User similarity, collaborative filtering |

## Usage Examples

### Create User with Brand

```python
from app.models import User, Brand

user = User(
    email="user@example.com",
    username="johndoe",
    password_hash="hashed_password",
    full_name="John Doe"
)

brand = Brand(
    user=user,
    name="TechCorp",
    description="Technology company",
    industry="Technology",
    tone="professional",
    embedding=[0.1, 0.2, ...]  # 384-dim vector
)

db.add(user)
await db.commit()
```

### Query with Vector Search

```python
from sqlalchemy import select
from app.models import Article

# Find similar articles
query_embedding = [0.1, 0.2, ...]  # 384-dim vector

result = await db.execute(
    select(Article)
    .order_by(Article.embedding.l2_distance(query_embedding))
    .limit(10)
)
articles = result.scalars().all()
```

### Track User Behavior

```python
from app.models import UserBehavior, ActionType

behavior = UserBehavior(
    user_id=user.id,
    article_id=article.id,
    action_type=ActionType.VIEW,
    time_spent=120,
    scroll_depth=0.75,
    device="mobile",
    platform="ios"
)

db.add(behavior)
await db.commit()
```

### Generate Post with Brand

```python
from app.models import GeneratedPost, PlatformType, PostStatus

post = GeneratedPost(
    user_id=user.id,
    brand_id=brand.id,
    platform=PlatformType.LINKEDIN,
    status=PostStatus.DRAFT,
    content="AI-generated post content",
    hashtags="#AI #Tech",
    ai_model="gpt-4",
    prompt_used="Generate a LinkedIn post about AI",
    embedding=[0.1, 0.2, ...]  # 384-dim vector
)

db.add(post)
await db.commit()
```

## Indexes

Recommended indexes for performance:

```sql
-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Brand indexes
CREATE INDEX idx_brands_user_id ON brands(user_id);

-- GeneratedPost indexes
CREATE INDEX idx_generated_posts_user_id ON generated_posts(user_id);
CREATE INDEX idx_generated_posts_brand_id ON generated_posts(brand_id);
CREATE INDEX idx_generated_posts_platform ON generated_posts(platform);
CREATE INDEX idx_generated_posts_status ON generated_posts(status);

-- Article indexes
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_articles_category ON articles(category);

-- Video indexes
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);

-- VideoScene indexes
CREATE INDEX idx_video_scenes_video_id ON video_scenes(video_id);

-- Caption indexes
CREATE INDEX idx_captions_video_id ON captions(video_id);

-- UserPreferences indexes
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

-- UserBehavior indexes
CREATE INDEX idx_user_behaviors_user_id ON user_behaviors(user_id);
CREATE INDEX idx_user_behaviors_article_id ON user_behaviors(article_id);

-- Vector indexes (IVFFlat for approximate search)
CREATE INDEX idx_brands_embedding ON brands USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
CREATE INDEX idx_generated_posts_embedding ON generated_posts USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
CREATE INDEX idx_articles_embedding ON articles USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
CREATE INDEX idx_videos_embedding ON videos USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
CREATE INDEX idx_video_scenes_embedding ON video_scenes USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
CREATE INDEX idx_user_preferences_embedding ON user_preferences USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

## Migration

Generate migration:

```bash
alembic revision --autogenerate -m "Create all models"
alembic upgrade head
```

## Summary

- ✅ 9 models implemented
- ✅ All models have id, created_at, updated_at
- ✅ Relationships properly defined
- ✅ 6 models with vector embeddings (384-dim)
- ✅ Support for semantic search
- ✅ Support for AI recommendations
- ✅ User behavior tracking
- ✅ UUIDs used for primary keys
- ✅ Enums for type safety
- ✅ Cascade deletes configured
