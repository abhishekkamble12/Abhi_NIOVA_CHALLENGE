# 🤖 AI Media OS – HiveMind

**Challenge Track**: Professional  
**Problem**: Content creators waste time using fragmented tools that don't learn from each other  
**Solution**: Unified AI platform where social media, news curation, and video editing share intelligence and improve together

> This is not automation.  
> This is a self-improving media intelligence layer.

📄 **[Requirements](requirements.md)** | 🏗️ **[Design](design.md)** | 📐 **[Architecture](ARCHITECTURE.md)** | 🗄️ **[Vector DB Setup](db-setup/)** | 🤖 **[Nova Integration](NOVA_INTEGRATION.md)**

---

## 🧠 What Makes It Different

Traditional tools operate in silos. AI Media OS connects them.

- 📹 Video insights → social captions  
- 📰 News trends → brand content ideas  
- 📈 Post performance → smarter future content  

Every module feeds the others.

---

## ⚙️ Core Capabilities

### 1. Intelligent Content Analysis
- Detects patterns in high-performing posts
- Learns from emojis, hooks, tone, and structure

### 2. Adaptive Content Generation
- Generates posts using real performance learnings
- Improves output quality with each iteration

### 3. Cross-Module Intelligence
- Shared memory across video, news, and social modules
- Compounding intelligence, not isolated AI calls

**Key Message:**  
> *“This system gets smarter every time you use it.”*

---

## 🏆 Why This Wins Hackathons & Competitions

### 🔧 Technical Excellence
- Event-driven architecture (not CRUD fluff)
- Async processing and clean separation of concerns
- Designed for microservices and scale

### 💼 Business Viability
- Targets $16B content marketing + $8B video editing markets
- Strong SaaS and enterprise licensing potential
- Defensible moat via learning loops

### 🚀 Innovation Factor
- End-to-end intelligence: creation → distribution → optimization
- Built AI-first, not retrofitted
- Compounding value with usage (network effects)

---

## 📋 Documentation

- **[requirements.md](requirements.md)** - Complete functional and non-functional requirements
- **[design.md](design.md)** - System design and architecture details
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Data flow patterns and implementation
- **[db-setup/](db-setup/)** - Vector database setup and configuration
- **[NOVA_INTEGRATION.md](NOVA_INTEGRATION.md)** - Complete Amazon Nova migration and API guide
- **[docs/AMAZON_NOVA_INTEGRATION.md](docs/AMAZON_NOVA_INTEGRATION.md)** - Quick Nova integration reference

---

## 🚀 Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python run.py

# Frontend
npm install
npm run dev
```

## Amazon Nova Integration

All AI operations in HiveMind are powered by **Amazon Nova** foundation models via AWS Bedrock:

| Capability | Model | API |
|---|---|---|
| **Text / Reasoning / Analysis** | Amazon Nova 2 Lite (`amazon.nova-2-lite-v1:0`) | Converse API |
| **Speech / Voice** | Amazon Nova 2 Sonic (`amazon.nova-2-sonic-v1:0`) | Converse API |
| **Embeddings / Vector Search** | Amazon Nova Multimodal Embeddings (`amazon.nova-2-multimodal-embeddings-v1:0`) | invoke_model |

### Why Nova?

- **Unified model family** — single vendor, consistent behavior across text, voice, and embeddings
- **Converse API** — standardized request/response format, no model-specific payload gymnastics
- **Multimodal embeddings** — text + image in a single 1024-dim vector space for richer semantic search
- **Cost-effective** — Nova 2 Lite delivers strong reasoning at a fraction of larger model costs

### Central AI Service

All modules call through `backend/ai/bedrock_nova_client.py`:

```python
from backend.ai.bedrock_nova_client import generate_text, generate_embeddings

content = generate_text("Write a LinkedIn post about AI trends")
vector  = generate_embeddings("semantic search query")
```

---

## Key Features

### Social Media Engine
- AI-powered content generation for Instagram, LinkedIn, X (Nova 2 Lite)
- Automatic engagement tracking and learning
- Platform-specific optimization

### Personalized News Feed
- NLP-based article analysis and tagging (Nova 2 Lite)
- Vector embeddings for semantic search via pgvector (Nova Multimodal Embeddings, 1024-dim)
- Hybrid recommendation engine (collaborative + vector similarity)
- Real-time user behavior learning

### Video Intelligence
- Automated scene detection and suggestions
- Speech-to-text captioning (AWS Transcribe + Nova 2 Sonic roadmap)
- Platform-optimized exports

### Cross-Module Learning
- Shared intelligence layer across all modules
- Performance insights improve all content types
- Compounding improvements over time
