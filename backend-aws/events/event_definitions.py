"""EventBridge Event Definitions and Patterns"""

# Event patterns for EventBridge rules
EVENT_PATTERNS = {
    "article_created": {
        "source": ["hivemind"],
        "detail-type": ["ArticleCreated"]
    },
    "article_viewed": {
        "source": ["hivemind"],
        "detail-type": ["ArticleViewed"]
    },
    "post_created": {
        "source": ["hivemind"],
        "detail-type": ["PostCreated"]
    },
    "post_engagement": {
        "source": ["hivemind"],
        "detail-type": ["PostEngagement"]
    },
    "video_uploaded": {
        "source": ["hivemind"],
        "detail-type": ["VideoUploaded"]
    },
    "video_processed": {
        "source": ["hivemind"],
        "detail-type": ["VideoProcessed"]
    }
}

# Example event payloads
EXAMPLE_EVENTS = {
    "ArticleCreated": {
        "version": "0",
        "id": "12345678-1234-1234-1234-123456789012",
        "detail-type": "ArticleCreated",
        "source": "hivemind",
        "account": "123456789012",
        "time": "2024-01-15T12:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {
            "article_id": 123,
            "title": "AI Trends 2024",
            "content": "Article content here...",
            "category": "technology",
            "timestamp": "2024-01-15T12:00:00Z"
        }
    },
    "VideoUploaded": {
        "version": "0",
        "id": "12345678-1234-1234-1234-123456789012",
        "detail-type": "VideoUploaded",
        "source": "hivemind",
        "account": "123456789012",
        "time": "2024-01-15T12:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {
            "video_id": 456,
            "s3_key": "videos/2024/01/15/video.mp4",
            "duration": 120.5,
            "timestamp": "2024-01-15T12:00:00Z"
        }
    },
    "PostEngagement": {
        "version": "0",
        "id": "12345678-1234-1234-1234-123456789012",
        "detail-type": "PostEngagement",
        "source": "hivemind",
        "account": "123456789012",
        "time": "2024-01-15T12:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {
            "post_id": 789,
            "likes": 150,
            "comments": 25,
            "shares": 10,
            "timestamp": "2024-01-15T12:00:00Z"
        }
    }
}
