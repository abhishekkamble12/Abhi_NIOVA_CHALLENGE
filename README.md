# 🤖 AI Media OS – HiveMind

**Challenge Track:** Professional
**Category:** AI / Content Intelligence Platform
**Powered by:** Amazon Nova (AWS Bedrock)

Deployed URL : http://hivemind-frontend-83016.s3-website.ap-south-1.amazonaws.com/

---

# 🚀 Overview

**HiveMind** is a unified **AI Media Operating System** where social media, news curation, and video intelligence **share knowledge and improve together**.

Traditional content tools operate in silos.

HiveMind connects them into a **self-improving intelligence layer**.

📹 Video insights → generate social media captions
📰 News trends → inspire brand content ideas
📈 Post performance → improve future content automatically

> **This is not automation.
> This is a self-improving media intelligence system.**

---

# ❗ Problem

Content creators and marketing teams use **fragmented tools**:

• Social media schedulers
• Video editors
• News monitoring tools
• Analytics dashboards

These tools **do not learn from each other**.

Result:

* wasted time
* inconsistent content quality
* no learning loop

The modern creator ecosystem needs a **connected AI intelligence layer**.

---

# 💡 Solution

HiveMind builds a **shared AI brain for media creation**.

Every module contributes knowledge:

```
Content Creation
      ↓
Performance Analysis
      ↓
AI Pattern Detection
      ↓
Smarter Future Content
```

Instead of isolated AI calls, HiveMind creates **compounding intelligence**.

---

# 🎥 Demo

**Demo Video**

https://youtu.be/3PtygnI6EEc

---

# 📸 Screenshots

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)

### AI Content Generator

![Generator](docs/screenshots/generator.png)

### Social Insights Engine

![Insights](docs/screenshots/insights.png)

---

# 🧠 Key Capabilities

## 1️⃣ Intelligent Content Analysis

HiveMind analyzes high-performing posts to detect patterns:

• tone
• emojis
• hooks
• storytelling structure
• engagement triggers

The system continuously learns what works best.

---

## 2️⃣ Adaptive Content Generation

Using learned patterns, HiveMind generates:

• LinkedIn posts
• Twitter threads
• Instagram captions
• brand marketing content

Each generation improves from **historical performance data**.

---

## 3️⃣ Cross-Module Intelligence

Modules share a **unified learning memory**.

```
Video Insights
      ↓
Content Generator
      ↓
Social Performance
      ↓
Learning Engine
```

This creates a **continuous feedback loop**.

---

# 🏗️ System Architecture

```
               User
                │
                ▼
          Frontend (React)
                │
                ▼
        API Gateway / Backend
           (Python / FastAPI)
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
  Social AI   News AI   Video AI
        │       │        │
        └───────┼────────┘
                ▼
        AI Intelligence Layer
           Amazon Nova Models
                │
                ▼
         Vector Database
             (pgvector)
```

---


---

# 🤖 Amazon Nova Integration

HiveMind uses **Amazon Nova foundation models via AWS Bedrock**.

| Capability                   | Model                      | API          |
| ---------------------------- | -------------------------- | ------------ |
| Text reasoning & analysis    | Amazon Nova 2 Lite         | Converse API |
| Speech / voice               | Amazon Nova 2 Sonic        | Converse API |
| Embeddings / semantic search | Nova Multimodal Embeddings | invoke_model |

---

## Why Amazon Nova?

• unified model ecosystem
• strong reasoning with low cost
• consistent API across models
• powerful multimodal embeddings

Nova enables HiveMind to operate as a **scalable AI intelligence layer**.

---

# 🧠 Central AI Service

All AI interactions pass through a **central Nova client**.

```
backend/ai/bedrock_nova_client.py
```

Example usage:

```python
from backend.ai.bedrock_nova_client import generate_text, generate_embeddings

content = generate_text("Write a LinkedIn post about AI trends")

vector = generate_embeddings("semantic search query")
```

This ensures **consistent AI orchestration across modules**.

---

# ⚙️ Core Modules

## 📱 Social Media Engine

AI-powered content generation.

Features:

• Instagram caption generator
• LinkedIn post writer
• X (Twitter) thread generation
• engagement analytics

---

## 📰 Personalized News Intelligence

Analyzes global news to generate **content inspiration**.

Capabilities:

• article NLP analysis
• topic clustering
• trend detection
• semantic search via embeddings

Vector storage powered by **pgvector**.

---

## 🎬 Video Intelligence

Helps creators repurpose videos for social media.

Features:

• scene detection
• caption generation
• speech-to-text
• social media export formats

---

## 🔄 Cross-Module Learning Engine

The core innovation of HiveMind.

All modules contribute to a **shared learning memory**.

```
User Content
      ↓
Performance Tracking
      ↓
AI Pattern Extraction
      ↓
Knowledge Storage
      ↓
Improved Future Content
```

This creates **compounding intelligence** over time.

---

# 📂 Project Structure

```
AI-Media-OS-HiveMind
│
├── backend
│   ├── ai
│   │   └── bedrock_nova_client.py
│   ├── routes
│   ├── services
│   └── run.py
│
├── frontend
│   └── React application
│
├── docs
│   ├── architecture.md
│   ├── requirements.md
│   └── AMAZON_NOVA_INTEGRATION.md
│
├── db-setup
│   └── vector database setup
│
└── README.md
```

---

# 🗄️ Vector Database

HiveMind uses **pgvector** for semantic search.

Embeddings generated using:

```
Amazon Nova Multimodal Embeddings
```

Vector dimension:

```
1024
```

This enables:

• semantic search
• content similarity detection
• personalized recommendations

---

# ⚡ Quick Start

## Backend

```
cd backend
pip install -r requirements.txt
python run.py
```

## Frontend

```
npm install
npm run dev
```

---

# 🔮 Future Improvements

• automated content scheduling
• AI video editing assistant
• brand voice training models
• creator collaboration intelligence
• AI influencer trend prediction

---

# 🏆 Why HiveMind Matters

The creator economy is rapidly expanding.

But creators lack **intelligent systems that learn from their own content**.

HiveMind introduces a new concept:

> **A Media Operating System that continuously improves itself.**

---

# 👨‍💻 Built For

Amazon Nova AI Hackathon

---

# 📄 License

MIT License
