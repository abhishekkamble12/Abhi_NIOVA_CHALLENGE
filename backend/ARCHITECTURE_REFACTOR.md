# Backend Architecture Refactoring Guide

## Overview

Refactored FastAPI backend to follow production-grade architecture with proper separation of concerns, dependency injection, and thin controllers.

## New Folder Structure

```
backend/app/
├── core/                      # Core infrastructure
│   ├── config.py             # Configuration management
│   ├── database.py           # Database connection
│   ├── redis.py              # Redis client
│   ├── logging.py            # Logging setup
│   ├── middleware.py         # Request logging middleware
│   └── exceptions.py         # Global exception handling
│
├── models/                    # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py
│   ├── brand.py
│   ├── article.py
│   ├── generated_post.py
│   ├── video.py
│   ├── video_scene.py
│   ├── caption.py
│   ├── user_preferences.py
│   └── user_behavior.py
│
├── schemas/                   # Pydantic request/response schemas
│   ├── __init__.py
│   ├── brand.py              # Brand schemas
│   └── article.py            # Article schemas
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── brand_service.py      # Brand business logic
│   ├── article_service.py    # Article business logic
│   └── vector_service.py     # Vector embedding service
│
├── api/                       # API layer
│   └── v1/
│       ├── router.py         # Main API router
│       └── endpoints/        # Thin endpoint controllers
│           ├── brands.py     # Brand endpoints
│           └── articles.py   # Article endpoints
│
├── examples/                  # Usage examples
│   ├── logging_examples.py
│   ├── exception_examples.py
│   └── vector_service_examples.py
│
└── main.py                    # FastAPI application entry point
```

## Architecture Layers

### 1. Core Layer (`core/`)
**Purpose**: Infrastructure and cross-cutting concerns

- Configuration management
- Database connections
- Redis client
- Logging setup
- Middleware
- Exception handling

### 2. Models Layer (`models/`)
**Purpose**: Database schema definitions

- SQLAlchemy ORM models
- Database table definitions
- Relationships between entities
- No business logic

### 3. Schemas Layer (`schemas/`)
**Purpose**: Request/response validation

- Pydantic models for API contracts
- Input validation
- Output serialization
- Type safety

**Schema Types:**
- `Base` - Common fields
- `Create` - For POST requests
- `Update` - For PUT/PATCH requests
- `Response` - For API responses
- `ListResponse` - For paginated lists

### 4. Services Layer (`services/`)
**Purpose**: Business logic and data operations

- CRUD operations
- Business rules
- Data transformations
- External service integrations
- Reusable across endpoints

### 5. API Layer (`api/`)
**Purpose**: HTTP request handling

- Thin controllers
- Route definitions
- Request/response mapping
- Dependency injection
- No business logic

## Refactoring Example: Brand Management

### Before (Fat Controller)

```python
# Old: Business logic in endpoint
@router.post("/brands")
async def create_brand(brand_data: dict, db: AsyncSession = Depends(get_db)):
    # Validation
    if not brand_data.get("name"):
        raise HTTPException(400, "Name required")
    
    # Generate embedding
    text = f"{brand_data['name']} {brand_data.get('description', '')}"
    embedding = generate_embedding(text)
    
    # Create brand
    brand = Brand(
        name=brand_data["name"],
        description=brand_data.get("description"),
        embedding=embedding
    )
    
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    
    # Log
    logger.info(f"Brand created: {brand.id}")
    
    return brand
```

### After (Thin Controller + Service)

**1. Schema (`schemas/brand.py`)**
```python
class BrandCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = None
    tone: Optional[str] = None
```

**2. Service (`services/brand_service.py`)**
```python
class BrandService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_brand(self, user_id: UUID, brand_data: BrandCreate) -> Brand:
        # Generate embedding
        text = f"{brand_data.name} {brand_data.description or ''}"
        embedding = generate_embedding(text)
        
        # Create brand
        brand = Brand(
            user_id=user_id,
            name=brand_data.name,
            description=brand_data.description,
            embedding=embedding
        )
        
        self.db.add(brand)
        await self.db.commit()
        await self.db.refresh(brand)
        
        logger.info(f"Brand created: {brand.id}")
        return brand
```

**3. Endpoint (`api/v1/endpoints/brands.py`)**
```python
@router.post("", response_model=BrandResponse, status_code=201)
async def create_brand(
    brand_data: BrandCreate,
    user_id: UUID,
    brand_service: BrandService = Depends(get_brand_service)
):
    """Create a new brand"""
    return await brand_service.create_brand(user_id, brand_data)
```

## Key Principles

### 1. Separation of Concerns

**Models**: Database schema only
```python
class Brand(Base):
    __tablename__ = "brands"
    id = Column(UUID, primary_key=True)
    name = Column(String(255), nullable=False)
    # No business logic here
```

**Schemas**: Validation only
```python
class BrandCreate(BaseModel):
    name: str = Field(..., min_length=1)
    # Validation rules only
```

**Services**: Business logic only
```python
class BrandService:
    async def create_brand(self, ...):
        # Business logic here
        pass
```

**Endpoints**: HTTP handling only
```python
@router.post("")
async def create_brand(data, service=Depends(...)):
    return await service.create_brand(data)
```

### 2. Dependency Injection

**Service Factory:**
```python
def get_brand_service(db: AsyncSession = Depends(get_db)) -> BrandService:
    return BrandService(db)
```

**Usage in Endpoint:**
```python
async def create_brand(
    brand_service: BrandService = Depends(get_brand_service)
):
    return await brand_service.create_brand(...)
```

**Benefits:**
- Easy testing (mock services)
- Loose coupling
- Reusable services
- Clear dependencies

### 3. Thin Controllers

**Good (Thin):**
```python
@router.get("/{id}")
async def get_brand(id: UUID, service: BrandService = Depends(...)):
    return await service.get_brand(id)
```

**Bad (Fat):**
```python
@router.get("/{id}")
async def get_brand(id: UUID, db: AsyncSession = Depends(...)):
    result = await db.execute(select(Brand).filter(Brand.id == id))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(404)
    return brand
```

### 4. Schema-Driven Development

**Request Validation:**
```python
class BrandCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
```

**Response Serialization:**
```python
class BrandResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

**Automatic Validation:**
- FastAPI validates input automatically
- Type errors return 422 responses
- Clear error messages

## Migration Guide

### Step 1: Create Schemas

```python
# schemas/resource.py
class ResourceBase(BaseModel):
    field1: str
    field2: Optional[int] = None

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    field1: Optional[str] = None
    field2: Optional[int] = None

class ResourceResponse(ResourceBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

### Step 2: Create Service

```python
# services/resource_service.py
class ResourceService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: ResourceCreate) -> Resource:
        resource = Resource(**data.model_dump())
        self.db.add(resource)
        await self.db.commit()
        await self.db.refresh(resource)
        return resource
    
    async def get(self, id: UUID) -> Resource:
        result = await self.db.execute(
            select(Resource).filter(Resource.id == id)
        )
        resource = result.scalar_one_or_none()
        if not resource:
            raise NotFoundException(f"Resource {id} not found")
        return resource

def get_resource_service(db: AsyncSession = Depends(get_db)):
    return ResourceService(db)
```

### Step 3: Create Thin Endpoints

```python
# api/v1/endpoints/resources.py
router = APIRouter(prefix="/resources", tags=["resources"])

@router.post("", response_model=ResourceResponse, status_code=201)
async def create_resource(
    data: ResourceCreate,
    service: ResourceService = Depends(get_resource_service)
):
    return await service.create(data)

@router.get("/{id}", response_model=ResourceResponse)
async def get_resource(
    id: UUID,
    service: ResourceService = Depends(get_resource_service)
):
    return await service.get(id)
```

### Step 4: Register Router

```python
# api/v1/router.py
from app.api.v1.endpoints import resources

api_router = APIRouter()
api_router.include_router(resources.router)
```

## Testing Benefits

### Service Testing (Unit Tests)

```python
async def test_create_brand():
    # Mock database
    db = AsyncMock()
    service = BrandService(db)
    
    # Test business logic
    brand_data = BrandCreate(name="Test Brand")
    brand = await service.create_brand(user_id, brand_data)
    
    assert brand.name == "Test Brand"
    db.add.assert_called_once()
```

### Endpoint Testing (Integration Tests)

```python
def test_create_brand_endpoint():
    # Mock service
    mock_service = Mock()
    mock_service.create_brand.return_value = Brand(...)
    
    # Override dependency
    app.dependency_overrides[get_brand_service] = lambda: mock_service
    
    # Test endpoint
    response = client.post("/brands", json={"name": "Test"})
    assert response.status_code == 201
```

## Benefits Summary

✅ **Separation of Concerns** - Each layer has single responsibility  
✅ **Testability** - Easy to unit test services  
✅ **Reusability** - Services can be used across endpoints  
✅ **Maintainability** - Changes isolated to specific layers  
✅ **Type Safety** - Pydantic schemas provide validation  
✅ **Documentation** - Auto-generated OpenAPI docs  
✅ **Dependency Injection** - Loose coupling, easy mocking  
✅ **Thin Controllers** - Endpoints are simple and readable  

## File Checklist

- [x] `schemas/brand.py` - Brand request/response schemas
- [x] `schemas/article.py` - Article request/response schemas
- [x] `services/brand_service.py` - Brand business logic
- [x] `services/article_service.py` - Article business logic
- [x] `api/v1/endpoints/brands.py` - Brand endpoints
- [x] `api/v1/endpoints/articles.py` - Article endpoints
- [x] `api/v1/router.py` - Main API router

## Next Steps

1. Create schemas for remaining models (User, Video, etc.)
2. Create services for remaining models
3. Create thin endpoints for remaining resources
4. Add authentication/authorization middleware
5. Add rate limiting
6. Add caching decorators
7. Add comprehensive tests
