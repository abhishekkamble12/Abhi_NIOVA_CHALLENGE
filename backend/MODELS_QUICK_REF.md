# Models Quick Reference

## Import

```python
from app.models import (
    User, Brand, GeneratedPost, Article, Video,
    VideoScene, Caption, UserPreferences, UserBehavior,
    PlatformType, PostStatus, VideoStatus, ActionType
)
```

## Models Overview

| Model | Purpose | Vector Embedding |
|-------|---------|------------------|
| User | Authentication & profile | ❌ |
| Brand | Brand identity & voice | ✅ 384-dim |
| GeneratedPost | AI-generated posts | ✅ 384-dim |
| Article | News feed articles | ✅ 384-dim |
| Video | Video content | ✅ 384-dim |
| VideoScene | Scene detection | ✅ 384-dim |
| Caption | Video captions | ❌ |
| UserPreferences | User settings | ✅ 384-dim |
| UserBehavior | Interaction tracking | ❌ |

## Quick Examples

### Create User
```python
user = User(
    email="user@example.com",
    username="johndoe",
    password_hash="hashed_password"
)
db.add(user)
await db.commit()
```

### Create Brand with Embedding
```python
brand = Brand(
    user_id=user.id,
    name="TechCorp",
    industry="Technology",
    tone="professional",
    embedding=[0.1, 0.2, ...]  # 384-dim
)
```

### Generate Post
```python
post = GeneratedPost(
    user_id=user.id,
    brand_id=brand.id,
    platform=PlatformType.LINKEDIN,
    status=PostStatus.DRAFT,
    content="Post content",
    embedding=[0.1, 0.2, ...]
)
```

### Vector Search
```python
from sqlalchemy import select

# Find similar articles
result = await db.execute(
    select(Article)
    .order_by(Article.embedding.l2_distance(query_vector))
    .limit(10)
)
articles = result.scalars().all()
```

### Track Behavior
```python
behavior = UserBehavior(
    user_id=user.id,
    article_id=article.id,
    action_type=ActionType.VIEW,
    time_spent=120
)
```

## Relationships

```
User → brands → Brand → generated_posts → GeneratedPost
User → generated_posts → GeneratedPost
User → preferences → UserPreferences
User → behaviors → UserBehavior → article → Article

Video → scenes → VideoScene
Video → captions → Caption
```

## Enums

```python
# Platform types
PlatformType.INSTAGRAM
PlatformType.LINKEDIN
PlatformType.TWITTER
PlatformType.FACEBOOK

# Post status
PostStatus.DRAFT
PostStatus.SCHEDULED
PostStatus.PUBLISHED
PostStatus.ARCHIVED

# Video status
VideoStatus.UPLOADING
VideoStatus.PROCESSING
VideoStatus.READY
VideoStatus.FAILED

# Action types
ActionType.VIEW
ActionType.CLICK
ActionType.LIKE
ActionType.SHARE
ActionType.SAVE
ActionType.DISMISS
```

## Common Fields

All models include:
- `id` (UUID) - Primary key
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

## Files

- `app/models/*.py` - Individual model files
- `app/models/__init__.py` - Model exports
- `MODELS.md` - Full documentation
