"""SQLAlchemy-compatible database service for Lambda"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'hiveminddb')
DB_USER = os.getenv('DB_USER', 'hivemind')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Engine with NullPool (no connection pooling for Lambda)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # No connection pooling in Lambda
    echo=False,
    connect_args={
        'connect_timeout': 5,
        'options': '-c timezone=utc'
    }
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for SQLAlchemy sessions.
    Automatically commits and closes session.
    
    Usage:
        with get_db_session() as session:
            brand = session.query(Brand).filter_by(id=brand_id).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def execute_raw_sql(query: str, params: dict = None):
    """
    Execute raw SQL query.
    
    Usage:
        result = execute_raw_sql(
            "SELECT * FROM brands WHERE id = :id",
            {"id": brand_id}
        )
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        conn.commit()
        return result


# ==================== Example Usage with SQLAlchemy Models ====================

"""
# Define models (if using SQLAlchemy ORM)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Text

Base = declarative_base()

class Brand(Base):
    __tablename__ = 'brands'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    created_at = Column(DateTime)

# Usage in Lambda handler
def handler(event, context):
    with get_db_session() as session:
        # Query
        brand = session.query(Brand).filter_by(id='brand-123').first()
        
        # Create
        new_brand = Brand(id='brand-456', name='TechCorp', industry='tech')
        session.add(new_brand)
        
        # Update
        brand.name = 'Updated Name'
        
        # Delete
        session.delete(brand)
    
    return {'statusCode': 200}
"""
