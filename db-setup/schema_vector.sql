-- Vector Database Schema Setup for AI Media OS
-- This script adds vector embedding support to existing tables

-- ============================================
-- 1. ENABLE PGVECTOR EXTENSION
-- ============================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 2. ADD VECTOR COLUMNS TO EXISTING TABLES
-- ============================================

-- Articles: Store article content embeddings for semantic search
ALTER TABLE articles 
ADD COLUMN IF NOT EXISTS embedding vector(384);

-- Generated Posts: Store post embeddings for pattern matching
ALTER TABLE generated_posts 
ADD COLUMN IF NOT EXISTS embedding vector(384);

-- Video Scenes: Store scene embeddings for similarity detection
ALTER TABLE video_scenes 
ADD COLUMN IF NOT EXISTS embedding vector(384);

-- ============================================
-- 3. CREATE NEW VECTOR-SPECIFIC TABLES
-- ============================================

-- User Interest Embeddings: Aggregate user preferences as vectors
CREATE TABLE IF NOT EXISTS user_interest_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL,
    interest_category VARCHAR(100) DEFAULT 'general',
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, interest_category)
);

-- Content Similarity Cache: Pre-computed similar content pairs
CREATE TABLE IF NOT EXISTS content_similarity_cache (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL, -- 'article', 'post', 'video'
    source_id INTEGER NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id INTEGER NOT NULL,
    similarity_score FLOAT NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_type, source_id, target_type, target_id)
);

-- Cross-Module Intelligence: Link related content across modules
CREATE TABLE IF NOT EXISTS cross_module_links (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES generated_posts(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    link_type VARCHAR(50) NOT NULL, -- 'semantic', 'topic', 'trend'
    similarity_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. CREATE VECTOR INDEXES FOR FAST SEARCH
-- ============================================

-- Articles: IVFFlat index for approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS articles_embedding_idx 
ON articles 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Generated Posts: IVFFlat index
CREATE INDEX IF NOT EXISTS generated_posts_embedding_idx 
ON generated_posts 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Video Scenes: IVFFlat index
CREATE INDEX IF NOT EXISTS video_scenes_embedding_idx 
ON video_scenes 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 50);

-- User Interest Embeddings: IVFFlat index
CREATE INDEX IF NOT EXISTS user_interest_embeddings_idx 
ON user_interest_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 50);

-- ============================================
-- 5. CREATE HELPER INDEXES
-- ============================================

-- Index for user lookup
CREATE INDEX IF NOT EXISTS user_interest_embeddings_user_id_idx 
ON user_interest_embeddings(user_id);

-- Index for similarity cache lookups
CREATE INDEX IF NOT EXISTS content_similarity_cache_source_idx 
ON content_similarity_cache(source_type, source_id);

CREATE INDEX IF NOT EXISTS content_similarity_cache_target_idx 
ON content_similarity_cache(target_type, target_id);

-- Index for cross-module links
CREATE INDEX IF NOT EXISTS cross_module_links_article_idx 
ON cross_module_links(article_id);

CREATE INDEX IF NOT EXISTS cross_module_links_post_idx 
ON cross_module_links(post_id);

CREATE INDEX IF NOT EXISTS cross_module_links_video_idx 
ON cross_module_links(video_id);

-- ============================================
-- 6. CREATE HELPER FUNCTIONS
-- ============================================

-- Function to find similar articles
CREATE OR REPLACE FUNCTION find_similar_articles(
    query_embedding vector(384),
    similarity_threshold FLOAT DEFAULT 0.7,
    result_limit INT DEFAULT 10
)
RETURNS TABLE (
    article_id INT,
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id,
        1 - (embedding <=> query_embedding) as similarity
    FROM articles
    WHERE embedding IS NOT NULL
    AND 1 - (embedding <=> query_embedding) > similarity_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to find similar posts
CREATE OR REPLACE FUNCTION find_similar_posts(
    query_embedding vector(384),
    result_limit INT DEFAULT 5
)
RETURNS TABLE (
    post_id INT,
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id,
        1 - (embedding <=> query_embedding) as similarity
    FROM generated_posts
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> query_embedding
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's personalized content
CREATE OR REPLACE FUNCTION get_personalized_articles(
    p_user_id INT,
    result_limit INT DEFAULT 20
)
RETURNS TABLE (
    article_id INT,
    relevance_score FLOAT
) AS $$
DECLARE
    user_embedding vector(384);
BEGIN
    -- Get user's interest embedding
    SELECT embedding INTO user_embedding
    FROM user_interest_embeddings
    WHERE user_id = p_user_id
    ORDER BY updated_at DESC
    LIMIT 1;
    
    -- If no user embedding, return recent articles
    IF user_embedding IS NULL THEN
        RETURN QUERY
        SELECT id, 0.5::FLOAT
        FROM articles
        ORDER BY published_date DESC
        LIMIT result_limit;
    ELSE
        -- Return similar articles
        RETURN QUERY
        SELECT 
            id,
            1 - (embedding <=> user_embedding) as relevance
        FROM articles
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> user_embedding
        LIMIT result_limit;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 7. CREATE TRIGGERS FOR AUTO-UPDATE
-- ============================================

-- Trigger to update user_interest_embeddings timestamp
CREATE OR REPLACE FUNCTION update_user_interest_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_interest_embeddings_update_trigger
BEFORE UPDATE ON user_interest_embeddings
FOR EACH ROW
EXECUTE FUNCTION update_user_interest_timestamp();

-- ============================================
-- 8. CREATE VIEWS FOR ANALYTICS
-- ============================================

-- View: Articles with embedding status
CREATE OR REPLACE VIEW articles_embedding_status AS
SELECT 
    COUNT(*) as total_articles,
    COUNT(embedding) as articles_with_embeddings,
    ROUND(100.0 * COUNT(embedding) / COUNT(*), 2) as embedding_coverage_percent
FROM articles;

-- View: User interest profile completeness
CREATE OR REPLACE VIEW user_interest_profile_status AS
SELECT 
    u.id as user_id,
    u.email,
    COUNT(uie.id) as interest_categories,
    MAX(uie.updated_at) as last_profile_update
FROM users u
LEFT JOIN user_interest_embeddings uie ON u.id = uie.user_id
GROUP BY u.id, u.email;

-- View: Cross-module content connections
CREATE OR REPLACE VIEW cross_module_connections AS
SELECT 
    'article_to_post' as connection_type,
    COUNT(*) as connection_count,
    AVG(similarity_score) as avg_similarity
FROM cross_module_links
WHERE article_id IS NOT NULL AND post_id IS NOT NULL
UNION ALL
SELECT 
    'article_to_video' as connection_type,
    COUNT(*) as connection_count,
    AVG(similarity_score) as avg_similarity
FROM cross_module_links
WHERE article_id IS NOT NULL AND video_id IS NOT NULL
UNION ALL
SELECT 
    'post_to_video' as connection_type,
    COUNT(*) as connection_count,
    AVG(similarity_score) as avg_similarity
FROM cross_module_links
WHERE post_id IS NOT NULL AND video_id IS NOT NULL;

-- ============================================
-- 9. GRANT PERMISSIONS
-- ============================================

-- Grant permissions to application user (adjust username as needed)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;

-- ============================================
-- 10. VERIFICATION QUERIES
-- ============================================

-- Check if pgvector is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check vector columns
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE data_type = 'USER-DEFINED' 
AND udt_name = 'vector';

-- Check vector indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexdef LIKE '%vector%';

-- Check embedding coverage
SELECT * FROM articles_embedding_status;

-- ============================================
-- NOTES
-- ============================================

-- Index tuning recommendations:
-- - For < 100K vectors: lists = 100
-- - For 100K - 1M vectors: lists = 1000
-- - For > 1M vectors: consider Pinecone/Qdrant

-- Query performance tuning:
-- SET ivfflat.probes = 10;  -- Faster, less accurate
-- SET ivfflat.probes = 100; -- Slower, more accurate

-- Embedding dimensions:
-- - 384: all-MiniLM-L6-v2 (lightweight, fast)
-- - 768: all-mpnet-base-v2 (better quality)
-- - 1536: OpenAI text-embedding-ada-002 (best quality)
