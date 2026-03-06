from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.models import Article
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.services.vector_service import generate_embedding, search_similar_articles
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger

logger = get_logger(__name__)


class ArticleService:
    """Service for article business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_article(self, article_data: ArticleCreate) -> Article:
        """Create a new article with embedding"""
        
        # Generate embedding
        text_for_embedding = f"{article_data.title} {article_data.content}"
        embedding = generate_embedding(text_for_embedding)
        
        # Create article
        article = Article(
            title=article_data.title,
            content=article_data.content,
            summary=article_data.summary,
            url=article_data.url,
            source=article_data.source,
            author=article_data.author,
            category=article_data.category,
            tags=article_data.tags,
            embedding=embedding
        )
        
        self.db.add(article)
        await self.db.commit()
        await self.db.refresh(article)
        
        logger.info(f"Article created: {article.id}", extra={"extra_fields": {"article_id": str(article.id)}})
        
        return article
    
    async def get_article(self, article_id: UUID) -> Article:
        """Get article by ID"""
        
        result = await self.db.execute(
            select(Article).filter(Article.id == article_id)
        )
        article = result.scalar_one_or_none()
        
        if not article:
            raise NotFoundException(
                message=f"Article {article_id} not found",
                details={"article_id": str(article_id)}
            )
        
        return article
    
    async def list_articles(
        self,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Article], int]:
        """List articles with pagination"""
        
        # Build query
        query = select(Article)
        count_query = select(func.count()).select_from(Article)
        
        if category:
            query = query.filter(Article.category == category)
            count_query = count_query.filter(Article.category == category)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get articles
        query = query.offset(skip).limit(limit).order_by(Article.created_at.desc())
        result = await self.db.execute(query)
        articles = result.scalars().all()
        
        return list(articles), total
    
    async def search_articles(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.5
    ) -> List[Tuple[Article, float]]:
        """Search articles using semantic search"""
        
        results = await search_similar_articles(
            db=self.db,
            query_text=query,
            limit=limit,
            min_similarity=min_similarity
        )
        
        logger.info(
            f"Article search completed: {len(results)} results",
            extra={"extra_fields": {"query": query, "results_count": len(results)}}
        )
        
        return results
    
    async def update_article(
        self,
        article_id: UUID,
        article_data: ArticleUpdate
    ) -> Article:
        """Update article"""
        
        article = await self.get_article(article_id)
        
        # Update fields
        update_data = article_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        # Regenerate embedding if content changed
        if 'title' in update_data or 'content' in update_data:
            text_for_embedding = f"{article.title} {article.content}"
            article.embedding = generate_embedding(text_for_embedding)
        
        await self.db.commit()
        await self.db.refresh(article)
        
        logger.info(f"Article updated: {article.id}", extra={"extra_fields": {"article_id": str(article.id)}})
        
        return article
    
    async def delete_article(self, article_id: UUID) -> None:
        """Delete article"""
        
        article = await self.get_article(article_id)
        
        await self.db.delete(article)
        await self.db.commit()
        
        logger.info(f"Article deleted: {article_id}", extra={"extra_fields": {"article_id": str(article_id)}})
    
    async def increment_views(self, article_id: UUID) -> None:
        """Increment article view count"""
        
        article = await self.get_article(article_id)
        article.views += 1
        await self.db.commit()


# Dependency injection
def get_article_service(db: AsyncSession) -> ArticleService:
    """Get ArticleService instance"""
    return ArticleService(db)
