"""
Example usage of vector embedding service
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.vector_service import (
    generate_embedding,
    generate_batch_embeddings,
    search_similar_articles,
    search_similar_posts,
    search_similar_video_scenes
)
from app.models import Article, GeneratedPost

router = APIRouter()


# ============================================================================
# EXAMPLE 1: Generate Single Embedding
# ============================================================================

@router.post("/embeddings/generate")
async def generate_single_embedding(text: str):
    """Generate embedding for a single text"""
    
    embedding = generate_embedding(text)
    
    return {
        "text": text,
        "embedding": embedding,
        "dimension": len(embedding)
    }


# ============================================================================
# EXAMPLE 2: Generate Batch Embeddings
# ============================================================================

@router.post("/embeddings/batch")
async def generate_multiple_embeddings(texts: list[str]):
    """Generate embeddings for multiple texts efficiently"""
    
    embeddings = generate_batch_embeddings(texts, batch_size=32)
    
    return {
        "count": len(embeddings),
        "embeddings": embeddings,
        "dimension": len(embeddings[0]) if embeddings else 0
    }


# ============================================================================
# EXAMPLE 3: Search Similar Articles
# ============================================================================

@router.get("/articles/search")
async def semantic_article_search(
    query: str,
    limit: int = 10,
    min_similarity: float = 0.5,
    db: AsyncSession = Depends(get_db)
):
    """Search for similar articles using semantic search"""
    
    results = await search_similar_articles(
        db=db,
        query_text=query,
        limit=limit,
        min_similarity=min_similarity
    )
    
    return {
        "query": query,
        "count": len(results),
        "results": [
            {
                "id": str(article.id),
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "similarity": round(similarity, 4)
            }
            for article, similarity in results
        ]
    }


# ============================================================================
# EXAMPLE 4: Search Similar Posts
# ============================================================================

@router.get("/posts/search")
async def semantic_post_search(
    query: str,
    platform: str = None,
    limit: int = 10,
    min_similarity: float = 0.5,
    db: AsyncSession = Depends(get_db)
):
    """Search for similar generated posts"""
    
    results = await search_similar_posts(
        db=db,
        query_text=query,
        platform=platform,
        limit=limit,
        min_similarity=min_similarity
    )
    
    return {
        "query": query,
        "platform": platform,
        "count": len(results),
        "results": [
            {
                "id": str(post.id),
                "content": post.content[:200],
                "platform": post.platform.value,
                "engagement_rate": post.engagement_rate,
                "similarity": round(similarity, 4)
            }
            for post, similarity in results
        ]
    }


# ============================================================================
# EXAMPLE 5: Search Similar Video Scenes
# ============================================================================

@router.get("/video-scenes/search")
async def semantic_scene_search(
    query: str,
    video_id: str = None,
    limit: int = 10,
    min_similarity: float = 0.5,
    db: AsyncSession = Depends(get_db)
):
    """Search for similar video scenes"""
    
    results = await search_similar_video_scenes(
        db=db,
        query_text=query,
        video_id=video_id,
        limit=limit,
        min_similarity=min_similarity
    )
    
    return {
        "query": query,
        "video_id": video_id,
        "count": len(results),
        "results": [
            {
                "id": str(scene.id),
                "video_id": str(scene.video_id),
                "start_time": scene.start_time,
                "end_time": scene.end_time,
                "description": scene.description,
                "scene_type": scene.scene_type,
                "similarity": round(similarity, 4)
            }
            for scene, similarity in results
        ]
    }


# ============================================================================
# EXAMPLE 6: Create Article with Embedding
# ============================================================================

@router.post("/articles")
async def create_article_with_embedding(
    title: str,
    content: str,
    url: str,
    db: AsyncSession = Depends(get_db)
):
    """Create article with automatic embedding generation"""
    
    # Generate embedding from title + content
    text_for_embedding = f"{title} {content}"
    embedding = generate_embedding(text_for_embedding)
    
    # Create article
    article = Article(
        title=title,
        content=content,
        url=url,
        embedding=embedding
    )
    
    db.add(article)
    await db.commit()
    await db.refresh(article)
    
    return {
        "id": str(article.id),
        "title": article.title,
        "embedding_dimension": len(embedding)
    }


# ============================================================================
# EXAMPLE 7: Batch Create Articles with Embeddings
# ============================================================================

@router.post("/articles/batch")
async def create_articles_batch(
    articles_data: list[dict],
    db: AsyncSession = Depends(get_db)
):
    """Create multiple articles with batch embedding generation"""
    
    # Prepare texts for batch embedding
    texts = [
        f"{data['title']} {data['content']}"
        for data in articles_data
    ]
    
    # Generate embeddings in batch (efficient)
    embeddings = generate_batch_embeddings(texts, batch_size=32)
    
    # Create articles
    articles = []
    for data, embedding in zip(articles_data, embeddings):
        article = Article(
            title=data['title'],
            content=data['content'],
            url=data['url'],
            embedding=embedding
        )
        articles.append(article)
    
    db.add_all(articles)
    await db.commit()
    
    return {
        "count": len(articles),
        "articles": [
            {"id": str(article.id), "title": article.title}
            for article in articles
        ]
    }


# ============================================================================
# EXAMPLE 8: Find Similar Posts for Recommendation
# ============================================================================

@router.get("/posts/{post_id}/similar")
async def find_similar_posts(
    post_id: str,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """Find similar posts for recommendation"""
    
    from sqlalchemy import select
    from app.services.vector_service import vector_service
    
    # Get the source post
    result = await db.execute(
        select(GeneratedPost).filter(GeneratedPost.id == post_id)
    )
    source_post = result.scalar_one_or_none()
    
    if not source_post or not source_post.embedding:
        return {"error": "Post not found or has no embedding"}
    
    # Find similar posts using the embedding
    similar_posts = await vector_service.find_similar_by_embedding(
        db=db,
        embedding=source_post.embedding,
        model_class=GeneratedPost,
        limit=limit + 1,  # +1 to exclude self
        min_similarity=0.3
    )
    
    # Filter out the source post
    similar_posts = [
        (post, sim) for post, sim in similar_posts
        if str(post.id) != post_id
    ][:limit]
    
    return {
        "source_post_id": post_id,
        "similar_posts": [
            {
                "id": str(post.id),
                "content": post.content[:200],
                "platform": post.platform.value,
                "similarity": round(similarity, 4)
            }
            for post, similarity in similar_posts
        ]
    }


# ============================================================================
# EXAMPLE 9: Hybrid Search (Keyword + Semantic)
# ============================================================================

@router.get("/articles/hybrid-search")
async def hybrid_article_search(
    query: str,
    category: str = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Hybrid search combining keyword and semantic search"""
    
    from sqlalchemy import select, or_
    
    # Semantic search
    semantic_results = await search_similar_articles(
        db=db,
        query_text=query,
        limit=limit * 2,  # Get more for filtering
        min_similarity=0.3
    )
    
    # Filter by category if provided
    if category:
        semantic_results = [
            (article, sim) for article, sim in semantic_results
            if article.category == category
        ]
    
    # Keyword search for title/content
    keyword_query = select(Article).filter(
        or_(
            Article.title.ilike(f"%{query}%"),
            Article.content.ilike(f"%{query}%")
        )
    )
    
    if category:
        keyword_query = keyword_query.filter(Article.category == category)
    
    keyword_result = await db.execute(keyword_query.limit(limit))
    keyword_articles = keyword_result.scalars().all()
    
    # Combine results (deduplicate)
    seen_ids = set()
    combined_results = []
    
    # Add semantic results first
    for article, similarity in semantic_results:
        if str(article.id) not in seen_ids:
            combined_results.append({
                "id": str(article.id),
                "title": article.title,
                "url": article.url,
                "similarity": round(similarity, 4),
                "match_type": "semantic"
            })
            seen_ids.add(str(article.id))
    
    # Add keyword results
    for article in keyword_articles:
        if str(article.id) not in seen_ids:
            combined_results.append({
                "id": str(article.id),
                "title": article.title,
                "url": article.url,
                "similarity": None,
                "match_type": "keyword"
            })
            seen_ids.add(str(article.id))
    
    return {
        "query": query,
        "category": category,
        "count": len(combined_results[:limit]),
        "results": combined_results[:limit]
    }
