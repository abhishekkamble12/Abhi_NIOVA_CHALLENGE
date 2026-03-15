"""
Module B: Personalized News Feed System — Amazon Nova Edition
==============================================================
NLP, embeddings, recommendations, and personalization.
All AI calls use Amazon Nova models via Bedrock.

Models:
  Text/NLP → amazon.nova-2-lite-v1:0  (Converse API)
  Embeddings → amazon.nova-2-multimodal-embeddings-v1:0  (invoke_model)
"""

import boto3
import json
import os
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from enum import Enum
from botocore.config import Config as BotoConfig

# ---------------------------------------------------------------------------
# Bedrock client
# ---------------------------------------------------------------------------
_bedrock_config = BotoConfig(
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    retries={'max_attempts': 3, 'mode': 'adaptive'},
    read_timeout=120,
    connect_timeout=30,
)

_bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    config=_bedrock_config,
)

NOVA_TEXT_MODEL = os.environ.get('NOVA_TEXT_MODEL', 'amazon.nova-2-lite-v1:0')
NOVA_EMBEDDING_MODEL = os.environ.get(
    'NOVA_EMBEDDING_MODEL', 'amazon.nova-2-multimodal-embeddings-v1:0'
)
NOVA_EMBEDDING_DIMENSION = int(os.environ.get('NOVA_EMBEDDING_DIMENSION', '1024'))


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class NLPPipeline:
    """NLP processing for articles using Amazon Nova."""

    def __init__(self):
        self.bedrock = _bedrock_runtime
        self.embedding_dimension = NOVA_EMBEDDING_DIMENSION

    async def extract_tags(self, article_title: str, article_body: str) -> Dict:
        """Extract NLP tags from article using Nova 2 Lite."""
        prompt = f"""Analyze this article and extract key information:

Title: {article_title}
Body: {article_body[:500]}...

Extract and provide:
1. TOPICS: List 3-5 main topics (e.g., technology, finance, health)
2. ENTITIES: List 2-3 key entities (people, places, companies)
3. KEYWORDS: List 5-7 important keywords
4. SENTIMENT: positive, neutral, or negative
5. CATEGORY: Primary category (news, tech, business, entertainment, sports, health, science, politics, other)

Format as JSON with these keys."""

        try:
            response = await asyncio.to_thread(
                self.bedrock.converse,
                modelId=NOVA_TEXT_MODEL,
                messages=[
                    {'role': 'user', 'content': [{'text': prompt}]}
                ],
                system=[
                    {'text': 'You are an NLP expert. Extract tags and metadata from articles accurately. Return valid JSON only.'}
                ],
                inferenceConfig={
                    'temperature': 0.3,
                    'maxTokens': 200,
                },
            )

            tags_json = response['output']['message']['content'][0]['text']
            usage = response.get('usage', {})
            tags = json.loads(tags_json)

            return {
                "status": "success",
                "topics": tags.get("TOPICS", []),
                "entities": tags.get("ENTITIES", []),
                "keywords": tags.get("KEYWORDS", []),
                "sentiment": tags.get("SENTIMENT", "neutral").lower(),
                "category": tags.get("CATEGORY", "other").lower(),
                "tokens_used": usage.get('inputTokens', 0) + usage.get('outputTokens', 0),
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def generate_embedding(self, text: str) -> Dict:
        """Generate semantic embedding using Amazon Nova Multimodal Embeddings."""
        try:
            text = text[:3000]

            response = await asyncio.to_thread(
                self.bedrock.invoke_model,
                modelId=NOVA_EMBEDDING_MODEL,
                body=json.dumps({
                    'input': text,
                    'inputText': text,
                    'taskType': 'SINGLE_EMBEDDING',
                    'embeddingConfig': {
                        'outputEmbeddingLength': self.embedding_dimension,
                    },
                }),
            )

            result = json.loads(response['body'].read())
            embedding = result['embedding']

            return {
                "status": "success",
                "embedding": embedding,
                "dimension": len(embedding),
                "model": NOVA_EMBEDDING_MODEL,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def calculate_semantic_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings."""
        arr1 = np.array(embedding1)
        arr2 = np.array(embedding2)
        similarity = np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))
        return float(similarity)


class RecommendationEngine:
    """Hybrid recommendation engine (content-based + collaborative)."""

    def __init__(self):
        self.nlp_pipeline = NLPPipeline()
        self.content_weight = 0.6
        self.behavior_weight = 0.4
        self.novelty_factor = 0.2

    def content_based_score(
        self,
        article_tags: List[str],
        user_interests: List[str],
        article_embedding: List[float],
        user_interests_embedding: List[float],
    ) -> float:
        """Calculate content-based recommendation score."""
        common_tags = set(article_tags) & set(user_interests)
        tag_score = len(common_tags) / max(len(set(article_tags) | set(user_interests)), 1)

        if article_embedding and user_interests_embedding:
            embedding_score = self.nlp_pipeline.calculate_semantic_similarity(
                article_embedding, user_interests_embedding
            )
            embedding_score = (embedding_score + 1) / 2
        else:
            embedding_score = 0.5

        return 0.5 * tag_score + 0.5 * embedding_score

    def behavior_based_score(
        self, user_behavior: List[Dict], article_category: str
    ) -> float:
        """Calculate behavior-based recommendation score."""
        category_interactions = [
            b for b in user_behavior if b.get("category") == article_category
        ]

        if not category_interactions:
            return 0.3

        avg_read_time = np.mean(
            [b.get("read_time_seconds", 0) for b in category_interactions]
        )
        interaction_count = len(category_interactions)

        read_time_score = min(avg_read_time / 180, 1.0)
        recency_score = min(interaction_count / 10, 1.0)

        return 0.5 * read_time_score + 0.5 * recency_score

    def rank_articles(
        self,
        articles: List[Dict],
        user_interests: List[str],
        user_interests_embedding: List[float],
        user_behavior: List[Dict],
        limit: int = 10,
    ) -> List[Dict]:
        """Rank and return top articles for user."""
        scored_articles = []

        for article in articles:
            content_score = self.content_based_score(
                article_tags=article.get("tags", []),
                user_interests=user_interests,
                article_embedding=article.get("embedding", []),
                user_interests_embedding=user_interests_embedding,
            )

            behavior_score = self.behavior_based_score(
                user_behavior=user_behavior,
                article_category=article.get("category", "other"),
            )

            hybrid_score = (
                self.content_weight * content_score
                + self.behavior_weight * behavior_score
            )

            underexplored = self._is_underexplored_category(
                article.get("category"), user_behavior
            )
            if underexplored:
                hybrid_score = (hybrid_score * (1 - self.novelty_factor)) + self.novelty_factor

            scored_articles.append({
                **article,
                "recommendation_score": float(hybrid_score),
                "content_score": float(content_score),
                "behavior_score": float(behavior_score),
                "is_exploratory": underexplored,
            })

        ranked = sorted(
            scored_articles, key=lambda x: x["recommendation_score"], reverse=True
        )
        return ranked[:limit]

    def _is_underexplored_category(
        self, category: str, user_behavior: List[Dict]
    ) -> bool:
        category_count = len(
            [b for b in user_behavior if b.get("category") == category]
        )
        return category_count < 5


class UserProfileManager:
    """Manage user profiles and interest evolution."""

    def __init__(self):
        self.nlp_pipeline = NLPPipeline()

    async def build_user_profile(
        self, user_id: str, user_behaviors: List[Dict]
    ) -> Dict:
        """Dynamically build user profile from behavior."""
        if not user_behaviors:
            return {
                "user_id": user_id,
                "interests": [],
                "read_time_avg": 0,
                "engagement_preference": "medium",
                "last_updated": datetime.utcnow().isoformat(),
            }

        all_tags = []
        all_categories = []
        read_times = []

        for behavior in user_behaviors:
            all_tags.extend(behavior.get("article_tags", []))
            all_categories.append(behavior.get("category", "other"))
            read_times.append(behavior.get("read_time_seconds", 0))

        from collections import Counter

        tag_frequency = Counter(all_tags)
        top_interests = [tag for tag, _ in tag_frequency.most_common(10)]

        avg_read_time = np.mean(read_times) if read_times else 0
        if avg_read_time > 300:
            engagement_preference = "high"
        elif avg_read_time > 120:
            engagement_preference = "medium"
        else:
            engagement_preference = "low"

        interests_text = " ".join(top_interests)
        embedding_result = await self.nlp_pipeline.generate_embedding(interests_text)

        return {
            "user_id": user_id,
            "interests": top_interests,
            "interests_embedding": embedding_result.get("embedding", []),
            "read_time_avg": float(avg_read_time),
            "engagement_preference": engagement_preference,
            "category_preferences": dict(Counter(all_categories).most_common(5)),
            "last_updated": datetime.utcnow().isoformat(),
        }

    async def update_interests(
        self, user_id: str, new_behavior: Dict, current_profile: Dict
    ) -> Dict:
        """Update user profile with new behavior."""
        if "behavior_history" not in current_profile:
            current_profile["behavior_history"] = []

        current_profile["behavior_history"].append(new_behavior)

        if len(current_profile["behavior_history"]) >= 5:
            updated_profile = await self.build_user_profile(
                user_id, current_profile["behavior_history"]
            )
            current_profile.update(updated_profile)
            current_profile["behavior_history"] = []

        return current_profile


class FeedAssemblyService:
    """Real-time feed generation and ranking."""

    def __init__(self):
        self.recommendation_engine = RecommendationEngine()
        self.user_profile_manager = UserProfileManager()

    async def generate_feed(
        self,
        user_id: str,
        articles: List[Dict],
        user_profile: Dict,
        limit: int = 20,
    ) -> Dict:
        """Generate personalized feed for user."""
        ranked_articles = self.recommendation_engine.rank_articles(
            articles=articles,
            user_interests=user_profile.get("interests", []),
            user_interests_embedding=user_profile.get("interests_embedding", []),
            user_behavior=user_profile.get("behavior_history", []),
            limit=limit,
        )

        return {
            "user_id": user_id,
            "articles": ranked_articles,
            "total_count": len(ranked_articles),
            "generated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "recommendation_sources": "hybrid (content + behavior + novelty)",
                "exploratory_articles": sum(
                    1 for a in ranked_articles if a.get("is_exploratory")
                ),
                "avg_score": np.mean(
                    [a.get("recommendation_score", 0) for a in ranked_articles]
                ),
            },
        }

    async def get_trending_articles(
        self, articles: List[Dict], limit: int = 5
    ) -> List[Dict]:
        """Get trending articles (high engagement, recent)."""
        trending = sorted(
            articles,
            key=lambda x: (
                x.get("engagement_score", 0),
                x.get("published_date", 0),
            ),
            reverse=True,
        )
        return trending[:limit]

    async def balance_feed(
        self,
        recommended: List[Dict],
        trending: List[Dict],
        ratio: float = 0.8,
    ) -> List[Dict]:
        """Balance personalized vs trending articles."""
        personalized_count = int(len(recommended) * ratio)
        trending_count = len(recommended) - personalized_count

        balanced = []
        for i, article in enumerate(recommended[:personalized_count]):
            balanced.append(article)
            if i < trending_count and i < len(trending):
                balanced.append(trending[i])

        return balanced
