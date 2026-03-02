Here is a **refined, more professional, and cleaner version** of your Contributing Guide — structured better, slightly more powerful in tone, and easier to read while keeping your vision strong.

---

# 🤝 Contributing to AI Media OS

Thank you for your interest in contributing to **AI Media OS** — an AI-native platform designed to build *compounding intelligence* in content creation.

We don’t just automate workflows.
We design **closed-loop learning systems** that improve over time.

---

# 🎯 Our Vision

AI Media OS is building the operating system for intelligent media creation.

Our platform connects:

* AI content generation
* Personalized feeds
* Video automation
* Cross-module learning

Every module feeds data back into the system — creating intelligence that compounds.

---

# 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ Content Engine  │ │ Feed Pipeline   │ │ Video Pipeline  ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 SHARED INTELLIGENCE LAYER                   │
│  • Cross-module insights   • Learning loops                 │
└─────────────────────────────────────────────────────────────┘
```

**Core Principle:**
Every feature must contribute to system-wide intelligence.

---

# 🚀 Getting Started

## 🔧 Prerequisites

* Python 3.9+
* Node.js 18+
* PostgreSQL 12+
* Redis 6+
* Git

---

## ⚙️ Local Development Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-org/ai-media-os.git
cd ai-media-os
```

---

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

---

### 3️⃣ Frontend Setup

```bash
cd app
npm install
npm run dev
```

---

### 4️⃣ Database Setup

```bash
createdb ai_media_os
alembic upgrade head
```

---

# 📁 Project Structure

```
ai-media-os/
├── app/                # Next.js frontend
├── backend/            # FastAPI backend
├── docs/               # Documentation
├── tests/              # Test files
└── scripts/            # Utility scripts
```

Each new module must follow this layered architecture.

---

# 🎨 Code Standards

We maintain strict code quality standards.

---

## 🐍 Backend (Python)

* Format using **Black**
* Follow PEP 8
* Use type hints
* Use async/await for I/O
* Add docstrings for public functions

```bash
black backend/
```

---

## ⚛️ Frontend (TypeScript)

* Strict mode enabled
* Functional components only
* Proper interfaces
* Use Prettier formatting

```bash
npx prettier --write app/
```

---

# 🧪 Testing Requirements

Testing is mandatory.

---

## Backend Testing

* Use pytest
* Test success and failure cases
* Mock AI services when needed

```bash
pytest backend/tests/
```

---

## Frontend Testing

* Jest
* React Testing Library

```bash
npm test
```

---

# 🔄 Contribution Workflow

## 1️⃣ Create an Issue First

Before coding:

* Check existing issues
* Clearly define the problem
* Add acceptance criteria

---

## 2️⃣ Branch Naming

```
feature/social-scheduler
fix/feed-ranking-bug
docs/api-update
```

---

## 3️⃣ Commit Messages (Conventional)

```
feat(feed): add personalization model
fix(video): resolve upload timeout
docs(readme): update setup instructions
```

---

## 4️⃣ Pull Request Checklist

* Tests pass
* Code follows style rules
* Documentation updated
* No breaking changes (or documented)
* Self-review completed

At least **one code review** required before merge.

---

# 🤖 AI Module Contribution Rules

When adding new AI features:

### ✅ Follow This Structure

```
backend/app/api/v1/endpoints/
backend/app/services/
backend/app/models/
backend/app/schemas/
app/components/
```

---

### ✅ Include Learning Loops

Every AI module must support:

* Feedback collection
* Performance tracking
* Insight sharing
* Retraining hooks (if applicable)

Closed-loop learning is mandatory.

---

# 🗄️ Database Changes

Use Alembic only.

```bash
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```

Always:

* Add indexes for frequent queries
* Maintain backward compatibility
* Avoid destructive migrations without review

---

# 🔒 Security Standards

* JWT authentication required
* Validate all input with Pydantic
* Limit content length
* Sanitize user-generated input
* Never expose API keys in frontend

Security reviews are required for:

* Auth changes
* Payment integrations
* AI model upgrades

---

# ⚡ Performance Standards

## Backend

* Async APIs
* Connection pooling
* Redis caching
* Query optimization

## Frontend

* Lazy loading
* Optimized bundles
* Loading states
* Error boundaries

---

# 📚 Documentation Rules

All new features must include:

* Code documentation
* API documentation
* Usage examples
* Updated README (if needed)

We use OpenAPI/Swagger for backend documentation.

---

# 🐛 Bug Report Template

```
## Description
## Steps to Reproduce
## Expected Behavior
## Actual Behavior
## Environment
## Screenshots / Logs
```

Always write a failing test before fixing a bug.

---

# 🚀 Release Process

We follow Semantic Versioning:

* MAJOR → Breaking change
* MINOR → New feature
* PATCH → Bug fix

Release checklist:

* Tests passing
* Docs updated
* Version bumped
* CHANGELOG updated
* Security reviewed

---

# 🤝 Community Guidelines

We expect:

* Respectful communication
* Constructive feedback
* Inclusion
* Professional collaboration

Help newcomers. Share knowledge. Build together.

---

# 🎉 Contributor Recognition

Contributors may be featured in:

* README.md
* Release notes
* Annual highlights
* Speaking opportunities

---

# 📬 Contact

* Maintainers: @Abhishek Kamble, @Prathamesh Taware
* Security: [security@ai-media-os.com](mailto:security@ai-media-os.com)
* General: [hello@ai-media-os.com](mailto:hello@ai-media-os.com)

---

# 🚀 Final Note

AI Media OS is more than a product.

It’s an intelligence engine.

Every contribution should make the system:

* Smarter
* Faster
* More adaptive

Together, we are building intelligence that compounds over time.

---

Tell me the tone you want.
