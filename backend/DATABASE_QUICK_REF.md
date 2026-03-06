# Database Quick Reference

## Import

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.core.database import get_db, Base
```

## Route Example

```python
@router.get("/items/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).filter(Item.id == item_id))
    return result.scalar_one_or_none()
```

## CRUD Operations

```python
# CREATE
item = Item(name="Test")
db.add(item)
await db.commit()
await db.refresh(item)

# READ
result = await db.execute(select(Item).filter(Item.id == 1))
item = result.scalar_one_or_none()

# UPDATE
item.name = "Updated"
await db.commit()

# DELETE
await db.delete(item)
await db.commit()
```

## Vector Search

```python
from pgvector.sqlalchemy import Vector

# Define model
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    embedding = Column(Vector(384))

# Search
result = await db.execute(
    select(Article)
    .order_by(Article.embedding.l2_distance(query_vector))
    .limit(10)
)
articles = result.scalars().all()
```

## Configuration

```bash
# .env
DATABASE_URL=sqlite+aiosqlite:///./hivemind.db
# or
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/hivemind
```

## Files

- `app/core/database.py` - Database infrastructure
- `app/models/example.py` - Example models with pgvector
- `DATABASE.md` - Full documentation
