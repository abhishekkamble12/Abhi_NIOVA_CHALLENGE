# 🤝 Contributing to AI Media OS

Thank you for your interest in contributing to AI Media OS! This document provides guidelines for contributing to our AI-native media platform.

## 🎯 Project Vision

AI Media OS is building the future of content creation through **closed-loop learning systems**. We're not just automating tasks - we're creating intelligence that compounds over time.

## 🏗️ Architecture Overview

Before contributing, understand our core architecture:

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
│  • Cross-module insights  • Learning loops                 │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** (Backend)
- **Node.js 18+** (Frontend)
- **PostgreSQL 12+** (Database)
- **Redis 6+** (Caching)
- **Git** (Version control)

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/ai-media-os.git
   cd ai-media-os
   ```

2. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python run.py
   ```

3. **Frontend setup**:
   ```bash
   cd app
   npm install
   npm run dev
   ```

4. **Database setup**:
   ```bash
   # Create database
   createdb ai_media_os
   
   # Run migrations (when available)
   alembic upgrade head
   ```

## 📁 Project Structure

```
ai-media-os/
├── app/                          # Next.js Frontend
│   ├── components/               # React components
│   │   ├── SocialMediaDashboard.tsx
│   │   ├── PersonalizedNewsFeed.tsx
│   │   ├── VideoEditor.tsx
│   │   └── IntelligenceDashboard.tsx
│   ├── lib/                      # Utilities
│   └── page.tsx                  # Main application
│
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/     # API endpoints
│   │   ├── models/               # SQLAlchemy models
│   │   ├── services/             # Business logic
│   │   ├── schemas/              # Pydantic schemas
│   │   └── core/                 # Core utilities
│   └── requirements.txt
│
├── docs/                         # Documentation
├── tests/                        # Test files
└── scripts/                      # Utility scripts
```

## 🎨 Code Style Guidelines

### Python (Backend)

**Use Black for formatting**:
```bash
pip install black
black backend/
```

**Follow PEP 8 with these specifics**:
- Line length: 88 characters (Black default)
- Use type hints for all functions
- Docstrings for all public functions
- Use async/await for I/O operations

**Example**:
```python
from typing import List, Optional
from pydantic import BaseModel

class ContentRequest(BaseModel):
    brand_id: int
    platform: str
    tone: Optional[str] = "casual"

async def generate_content(
    request: ContentRequest,
    user_id: int
) -> ContentResponse:
    """
    Generate platform-optimized content for a brand.
    
    Args:
        request: Content generation parameters
        user_id: ID of the requesting user
        
    Returns:
        Generated content with metadata
    """
    # Implementation here
    pass
```

### TypeScript (Frontend)

**Use Prettier for formatting**:
```bash
npm install --save-dev prettier
npx prettier --write app/
```

**Follow these conventions**:
- Use TypeScript strict mode
- Prefer functional components with hooks
- Use proper TypeScript interfaces
- Follow React best practices

**Example**:
```typescript
interface ContentGenerationProps {
  brandId: number;
  onContentGenerated: (content: GeneratedContent) => void;
}

export default function ContentGeneration({ 
  brandId, 
  onContentGenerated 
}: ContentGenerationProps) {
  const [loading, setLoading] = useState(false);
  
  const handleGenerate = async () => {
    setLoading(true);
    try {
      const content = await generateContent(brandId);
      onContentGenerated(content);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleGenerate} disabled={loading}>
      {loading ? 'Generating...' : 'Generate Content'}
    </button>
  );
}
```

## 🧪 Testing Guidelines

### Backend Testing

**Use pytest for testing**:
```bash
pip install pytest pytest-asyncio
pytest backend/tests/
```

**Test structure**:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestContentGeneration:
    def test_generate_content_success(self):
        response = client.post(
            "/api/v1/social/generate/content",
            json={"brand_id": 1, "platform": "instagram"}
        )
        assert response.status_code == 200
        assert "caption" in response.json()
    
    def test_generate_content_invalid_brand(self):
        response = client.post(
            "/api/v1/social/generate/content",
            json={"brand_id": 999, "platform": "instagram"}
        )
        assert response.status_code == 404
```

### Frontend Testing

**Use Jest and React Testing Library**:
```bash
npm install --save-dev jest @testing-library/react
npm test
```

**Test example**:
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import ContentGeneration from '../components/ContentGeneration';

describe('ContentGeneration', () => {
  it('generates content when button is clicked', async () => {
    const mockOnGenerated = jest.fn();
    
    render(
      <ContentGeneration 
        brandId={1} 
        onContentGenerated={mockOnGenerated} 
      />
    );
    
    const button = screen.getByText('Generate Content');
    fireEvent.click(button);
    
    expect(screen.getByText('Generating...')).toBeInTheDocument();
  });
});
```

## 🔄 Contribution Workflow

### 1. Issue Creation

Before starting work:
- Check existing issues to avoid duplication
- Create a detailed issue with:
  - Clear problem description
  - Expected behavior
  - Steps to reproduce (for bugs)
  - Acceptance criteria (for features)

### 2. Branch Naming

Use descriptive branch names:
```bash
# Features
git checkout -b feature/social-media-scheduling
git checkout -b feature/video-thumbnail-optimization

# Bug fixes
git checkout -b fix/feed-ranking-algorithm
git checkout -b fix/video-upload-timeout

# Documentation
git checkout -b docs/api-documentation-update
```

### 3. Commit Messages

Follow conventional commits:
```bash
# Features
git commit -m "feat(social): add Instagram story generation"
git commit -m "feat(feed): implement real-time personalization"

# Bug fixes
git commit -m "fix(video): resolve scene detection timeout"
git commit -m "fix(api): handle missing user preferences"

# Documentation
git commit -m "docs(readme): update installation instructions"
```

### 4. Pull Request Process

**PR Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

**Review Process**:
1. Automated checks must pass (linting, tests)
2. At least one code review required
3. All conversations resolved
4. Documentation updated if needed

## 🏗️ Architecture Contributions

### Adding New Modules

When adding new AI modules:

1. **Follow the pattern**:
   ```
   backend/app/api/v1/endpoints/new_module.py
   backend/app/services/new_module_service.py
   backend/app/models/new_module.py
   backend/app/schemas/new_module.py
   app/components/NewModule.tsx
   ```

2. **Implement feedback loops**:
   ```python
   # Always include learning mechanisms
   async def process_feedback(module_id: int, performance_data: dict):
       # Analyze performance
       # Update model parameters
       # Trigger retraining if needed
   ```

3. **Add cross-module intelligence**:
   ```python
   # Share insights with other modules
   async def share_insights(insights: List[Insight]):
       await orchestrator.distribute_insights(insights)
   ```

### Database Changes

**Use Alembic for migrations**:
```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head
```

**Migration example**:
```python
def upgrade():
    op.create_table(
        'new_module_data',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('data', sa.JSON),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )
    
    # Add indexes
    op.create_index('ix_new_module_user_id', 'new_module_data', ['user_id'])
```

## 🤖 AI Service Integration

### Adding New AI Services

**Service interface**:
```python
from abc import ABC, abstractmethod

class AIService(ABC):
    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        pass
    
    @abstractmethod
    async def learn_from_feedback(self, feedback: dict) -> None:
        pass

class NewAIService(AIService):
    async def process(self, input_data: dict) -> dict:
        # Implement AI processing
        return {"result": "processed_data"}
    
    async def learn_from_feedback(self, feedback: dict) -> None:
        # Implement learning logic
        pass
```

### Mock vs Real AI Services

**Development (Mock)**:
```python
class MockLLMService:
    async def generate_content(self, prompt: str) -> str:
        # Return realistic mock data
        return f"Generated content for: {prompt[:50]}..."
```

**Production (Real)**:
```python
class OpenAIService:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate_content(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

## 📊 Performance Guidelines

### Backend Performance

**Database Optimization**:
- Use indexes on frequently queried columns
- Implement pagination for large result sets
- Use connection pooling
- Cache expensive queries

**API Performance**:
- Use async/await for I/O operations
- Implement request caching
- Add response compression
- Monitor response times

### Frontend Performance

**React Optimization**:
- Use React.memo for expensive components
- Implement lazy loading for routes
- Optimize bundle size
- Use proper key props in lists

**User Experience**:
- Add loading states for all async operations
- Implement skeleton screens
- Use optimistic updates where appropriate
- Handle error states gracefully

## 🔒 Security Guidelines

### Backend Security

**Authentication**:
```python
from jose import JWTError, jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user(user_id)
    if user is None:
        raise credentials_exception
    return user
```

**Input Validation**:
```python
from pydantic import BaseModel, validator

class ContentRequest(BaseModel):
    brand_id: int
    platform: str
    content: str
    
    @validator('platform')
    def validate_platform(cls, v):
        allowed_platforms = ['instagram', 'linkedin', 'twitter']
        if v not in allowed_platforms:
            raise ValueError('Invalid platform')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if len(v) > 10000:
            raise ValueError('Content too long')
        return v
```

### Frontend Security

**API Calls**:
```typescript
// Always handle errors and validate responses
const apiCall = async (endpoint: string, data: any) => {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};
```

## 📚 Documentation Standards

### Code Documentation

**Python docstrings**:
```python
def calculate_engagement_score(
    likes: int, 
    comments: int, 
    shares: int,
    impressions: int
) -> float:
    """
    Calculate engagement score for social media content.
    
    Args:
        likes: Number of likes received
        comments: Number of comments received  
        shares: Number of shares/retweets
        impressions: Total number of impressions
        
    Returns:
        Engagement score between 0.0 and 1.0
        
    Raises:
        ValueError: If impressions is zero or negative
        
    Example:
        >>> calculate_engagement_score(100, 20, 5, 10000)
        0.0125
    """
    if impressions <= 0:
        raise ValueError("Impressions must be positive")
    
    total_engagement = likes + (comments * 2) + (shares * 3)
    return total_engagement / impressions
```

**TypeScript documentation**:
```typescript
/**
 * Generates content for multiple social media platforms
 * 
 * @param brandId - Unique identifier for the brand
 * @param platforms - Array of platform names to generate for
 * @param options - Additional generation options
 * @returns Promise resolving to generated content for each platform
 * 
 * @example
 * ```typescript
 * const content = await generateMultiPlatformContent(
 *   123, 
 *   ['instagram', 'linkedin'], 
 *   { tone: 'professional' }
 * );
 * ```
 */
async function generateMultiPlatformContent(
  brandId: number,
  platforms: string[],
  options: GenerationOptions = {}
): Promise<MultiPlatformContent> {
  // Implementation
}
```

### API Documentation

Use OpenAPI/Swagger for API documentation:
```python
@app.post("/api/v1/social/generate/content", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate platform-optimized social media content.
    
    This endpoint uses AI to generate captions, hashtags, and CTAs
    optimized for the specified platform and brand voice.
    
    - **brand_id**: ID of the brand to generate content for
    - **platform**: Target platform (instagram, linkedin, twitter)
    - **tone**: Optional tone override (casual, professional, playful)
    
    Returns generated content with engagement predictions.
    """
    return await content_service.generate(request, current_user.id)
```

## 🎯 Feature Request Process

### 1. Research Phase
- Validate the problem exists
- Research existing solutions
- Estimate development effort
- Consider impact on architecture

### 2. Design Phase
- Create technical design document
- Consider cross-module implications
- Plan database schema changes
- Design API endpoints

### 3. Implementation Phase
- Create feature branch
- Implement backend changes
- Implement frontend changes
- Add comprehensive tests
- Update documentation

### 4. Review Phase
- Code review by team members
- Testing in staging environment
- Performance impact assessment
- Security review if needed

## 🐛 Bug Report Guidelines

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g. macOS 12.0]
- Browser: [e.g. Chrome 96]
- Version: [e.g. v1.2.3]

## Additional Context
Screenshots, logs, or other relevant information
```

### Bug Fix Process

1. **Reproduce the bug** in development environment
2. **Write a failing test** that demonstrates the bug
3. **Fix the bug** with minimal changes
4. **Ensure the test passes** and no regressions
5. **Update documentation** if behavior changed

## 🚀 Release Process

### Version Numbering

We follow semantic versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers bumped
- [ ] Security review completed
- [ ] Performance benchmarks run
- [ ] Deployment scripts tested

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Celebrate diverse perspectives
- Maintain professional communication

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Discord**: Real-time community chat (if available)
- **Email**: security@ai-media-os.com for security issues

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Annual contributor highlights
- Conference speaking opportunities

## 📞 Contact

- **Maintainers**: @username1, @username2
- **Security**: security@ai-media-os.com
- **General**: hello@ai-media-os.com

---

Thank you for contributing to the future of AI-native media creation! 🚀

**Together, we're building intelligence that compounds over time.**