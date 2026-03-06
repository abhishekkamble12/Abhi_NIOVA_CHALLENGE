-- Database Schema for HiveMind Backend

-- Brands table
CREATE TABLE IF NOT EXISTS brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    tone VARCHAR(100),
    target_audience TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Social posts table
CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    platform VARCHAR(50),
    content TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Post engagement table
CREATE TABLE IF NOT EXISTS post_engagement (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES social_posts(id),
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    ctr FLOAT DEFAULT 0.0,
    tracked_at TIMESTAMP DEFAULT NOW()
);

-- Articles table
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,
    url VARCHAR(1000),
    source VARCHAR(255),
    category VARCHAR(100),
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,
    keywords TEXT,
    categories TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    s3_url VARCHAR(1000),
    filename VARCHAR(500),
    duration FLOAT DEFAULT 0.0,
    thumbnail_url VARCHAR(1000),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Video scenes table
CREATE TABLE IF NOT EXISTS video_scenes (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    start_time FLOAT,
    end_time FLOAT,
    confidence FLOAT,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Video captions table
CREATE TABLE IF NOT EXISTS video_captions (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    text TEXT,
    language VARCHAR(10) DEFAULT 'en',
    start_time FLOAT,
    end_time FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_articles_embedding ON articles USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_video_scenes_embedding ON video_scenes USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_social_posts_brand ON social_posts(brand_id);
CREATE INDEX IF NOT EXISTS idx_videos_created ON videos(created_at DESC);
