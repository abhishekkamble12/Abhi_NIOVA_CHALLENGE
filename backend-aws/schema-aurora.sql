-- HiveMind Aurora PostgreSQL Schema

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Brands table
CREATE TABLE brands (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social posts table
CREATE TABLE social_posts (
    id VARCHAR(36) PRIMARY KEY,
    brand_id VARCHAR(36) REFERENCES brands(id),
    platform VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    media_url VARCHAR(500),  -- S3 URL
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

CREATE INDEX idx_posts_brand ON social_posts(brand_id);
CREATE INDEX idx_posts_platform ON social_posts(platform);

-- Engagement metrics table
CREATE TABLE engagement (
    id VARCHAR(36) PRIMARY KEY,
    post_id VARCHAR(36) REFERENCES social_posts(id),
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_engagement_post ON engagement(post_id);

-- Videos table
CREATE TABLE videos (
    id VARCHAR(36) PRIMARY KEY,
    s3_url VARCHAR(500) NOT NULL,  -- S3 URL
    duration FLOAT,
    transcription TEXT,
    status VARCHAR(20) DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE INDEX idx_videos_status ON videos(status);

-- Articles table
CREATE TABLE articles (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000),
    category VARCHAR(100),
    published_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_articles_category ON articles(category);

-- User preferences (relational data only, activity in DynamoDB)
CREATE TABLE user_preferences (
    user_id VARCHAR(36) PRIMARY KEY,
    preferred_platforms TEXT[],
    preferred_categories TEXT[],
    notification_settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance analytics (aggregated data)
CREATE TABLE performance_analytics (
    id VARCHAR(36) PRIMARY KEY,
    brand_id VARCHAR(36) REFERENCES brands(id),
    platform VARCHAR(50),
    date DATE NOT NULL,
    total_posts INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    avg_engagement_rate FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_brand_date ON performance_analytics(brand_id, date);
