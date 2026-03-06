"""
Vector Database Migration Script
Migrates existing data to include vector embeddings
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from tqdm import tqdm

# Configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/aimedios"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions
BATCH_SIZE = 50

class VectorMigration:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✓ Loaded embedding model: {EMBEDDING_MODEL}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def migrate_articles(self):
        """Migrate articles table to include embeddings."""
        print("\n📰 Migrating articles...")
        
        with self.engine.connect() as conn:
            # Get articles without embeddings
            result = conn.execute(text("""
                SELECT id, title, body 
                FROM articles 
                WHERE embedding IS NULL
                ORDER BY id
            """))
            articles = result.fetchall()
            
            if not articles:
                print("  ✓ All articles already have embeddings")
                return
            
            print(f"  Found {len(articles)} articles to process")
            
            # Process in batches
            for i in tqdm(range(0, len(articles), BATCH_SIZE), desc="  Processing"):
                batch = articles[i:i+BATCH_SIZE]
                
                # Generate embeddings
                texts = [f"{a.title} {a.body[:500]}" for a in batch]
                embeddings = self.generate_embeddings(texts)
                
                # Update database
                for article, embedding in zip(batch, embeddings):
                    conn.execute(
                        text("""
                            UPDATE articles 
                            SET embedding = :embedding 
                            WHERE id = :id
                        """),
                        {"id": article.id, "embedding": str(embedding)}
                    )
                
                conn.commit()
            
            print(f"  ✓ Migrated {len(articles)} articles")
    
    def migrate_posts(self):
        """Migrate generated_posts table to include embeddings."""
        print("\n📱 Migrating social media posts...")
        
        with self.engine.connect() as conn:
            # Get posts without embeddings
            result = conn.execute(text("""
                SELECT id, caption, hashtags 
                FROM generated_posts 
                WHERE embedding IS NULL
                ORDER BY id
            """))
            posts = result.fetchall()
            
            if not posts:
                print("  ✓ All posts already have embeddings")
                return
            
            print(f"  Found {len(posts)} posts to process")
            
            # Process in batches
            for i in tqdm(range(0, len(posts), BATCH_SIZE), desc="  Processing"):
                batch = posts[i:i+BATCH_SIZE]
                
                # Generate embeddings
                texts = [f"{p.caption} {p.hashtags}" for p in batch]
                embeddings = self.generate_embeddings(texts)
                
                # Update database
                for post, embedding in zip(batch, embeddings):
                    conn.execute(
                        text("""
                            UPDATE generated_posts 
                            SET embedding = :embedding 
                            WHERE id = :id
                        """),
                        {"id": post.id, "embedding": str(embedding)}
                    )
                
                conn.commit()
            
            print(f"  ✓ Migrated {len(posts)} posts")
    
    def migrate_video_scenes(self):
        """Migrate video_scenes table to include embeddings."""
        print("\n🎬 Migrating video scenes...")
        
        with self.engine.connect() as conn:
            # Get scenes without embeddings
            result = conn.execute(text("""
                SELECT vs.id, v.title, vs.scene_type
                FROM video_scenes vs
                JOIN videos v ON vs.video_id = v.id
                WHERE vs.embedding IS NULL
                ORDER BY vs.id
            """))
            scenes = result.fetchall()
            
            if not scenes:
                print("  ✓ All video scenes already have embeddings")
                return
            
            print(f"  Found {len(scenes)} scenes to process")
            
            # Process in batches
            for i in tqdm(range(0, len(scenes), BATCH_SIZE), desc="  Processing"):
                batch = scenes[i:i+BATCH_SIZE]
                
                # Generate embeddings
                texts = [f"{s.title} {s.scene_type}" for s in batch]
                embeddings = self.generate_embeddings(texts)
                
                # Update database
                for scene, embedding in zip(batch, embeddings):
                    conn.execute(
                        text("""
                            UPDATE video_scenes 
                            SET embedding = :embedding 
                            WHERE id = :id
                        """),
                        {"id": scene.id, "embedding": str(embedding)}
                    )
                
                conn.commit()
            
            print(f"  ✓ Migrated {len(scenes)} video scenes")
    
    def create_user_interest_profiles(self):
        """Create initial user interest profiles based on behavior."""
        print("\n👤 Creating user interest profiles...")
        
        with self.engine.connect() as conn:
            # Get users with behavior data
            result = conn.execute(text("""
                SELECT DISTINCT ub.user_id
                FROM user_behavior ub
                WHERE NOT EXISTS (
                    SELECT 1 FROM user_interest_embeddings uie 
                    WHERE uie.user_id = ub.user_id
                )
            """))
            users = result.fetchall()
            
            if not users:
                print("  ✓ All users already have interest profiles")
                return
            
            print(f"  Found {len(users)} users to process")
            
            for user in tqdm(users, desc="  Processing"):
                user_id = user.user_id
                
                # Get articles user interacted with
                result = conn.execute(text("""
                    SELECT a.embedding, ub.action
                    FROM user_behavior ub
                    JOIN articles a ON ub.article_id = a.id
                    WHERE ub.user_id = :user_id 
                    AND a.embedding IS NOT NULL
                    ORDER BY ub.timestamp DESC
                    LIMIT 20
                """), {"user_id": user_id})
                
                interactions = result.fetchall()
                
                if not interactions:
                    continue
                
                # Calculate weighted average embedding
                embeddings = []
                weights = []
                
                for interaction in interactions:
                    # Parse embedding string to list
                    embedding = eval(interaction.embedding)
                    embeddings.append(embedding)
                    
                    # Weight by action type
                    weight = 1.0
                    if interaction.action == 'like':
                        weight = 2.0
                    elif interaction.action == 'share':
                        weight = 3.0
                    weights.append(weight)
                
                # Weighted average
                weighted_sum = np.zeros(384)
                total_weight = sum(weights)
                
                for embedding, weight in zip(embeddings, weights):
                    weighted_sum += np.array(embedding) * weight
                
                avg_embedding = (weighted_sum / total_weight).tolist()
                
                # Insert user interest embedding
                conn.execute(text("""
                    INSERT INTO user_interest_embeddings 
                    (user_id, embedding, interest_category, weight)
                    VALUES (:user_id, :embedding, 'general', :weight)
                    ON CONFLICT (user_id, interest_category) 
                    DO UPDATE SET 
                        embedding = :embedding,
                        weight = :weight,
                        updated_at = CURRENT_TIMESTAMP
                """), {
                    "user_id": user_id,
                    "embedding": str(avg_embedding),
                    "weight": total_weight
                })
                
                conn.commit()
            
            print(f"  ✓ Created profiles for {len(users)} users")
    
    def verify_migration(self):
        """Verify migration was successful."""
        print("\n✅ Verifying migration...")
        
        with self.engine.connect() as conn:
            # Check articles
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(embedding) as with_embeddings,
                    ROUND(100.0 * COUNT(embedding) / COUNT(*), 2) as coverage
                FROM articles
            """))
            stats = result.fetchone()
            print(f"  Articles: {stats.with_embeddings}/{stats.total} ({stats.coverage}%)")
            
            # Check posts
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(embedding) as with_embeddings,
                    ROUND(100.0 * COUNT(embedding) / COUNT(*), 2) as coverage
                FROM generated_posts
            """))
            stats = result.fetchone()
            print(f"  Posts: {stats.with_embeddings}/{stats.total} ({stats.coverage}%)")
            
            # Check video scenes
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(embedding) as with_embeddings,
                    ROUND(100.0 * COUNT(embedding) / COUNT(*), 2) as coverage
                FROM video_scenes
            """))
            stats = result.fetchone()
            print(f"  Video Scenes: {stats.with_embeddings}/{stats.total} ({stats.coverage}%)")
            
            # Check user profiles
            result = conn.execute(text("""
                SELECT COUNT(*) as total
                FROM user_interest_embeddings
            """))
            stats = result.fetchone()
            print(f"  User Profiles: {stats.total}")
    
    def run(self):
        """Run full migration."""
        print("🚀 Starting Vector Database Migration")
        print(f"   Database: {DATABASE_URL}")
        print(f"   Model: {EMBEDDING_MODEL}")
        
        try:
            self.migrate_articles()
            self.migrate_posts()
            self.migrate_video_scenes()
            self.create_user_interest_profiles()
            self.verify_migration()
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    migration = VectorMigration()
    migration.run()
