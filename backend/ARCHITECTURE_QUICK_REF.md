# Architecture Quick Reference

## Folder Structure

```
app/
├── core/          # Infrastructure (config, database, logging, exceptions)
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic request/response models
├── services/      # Business logic layer
├── api/v1/        # API endpoints (thin controllers)
└── main.py        # FastAPI app
```

## Request Flow

```
HTTP Request
    ↓
Endpoint (api/v1/endpoints/)
    ↓ (validates with schema)
Service (services/)
    ↓ (business logic)
Model (models/)
    ↓ (database)
Database
    ↓
Model → Service → Endpoint → HTTP Response
```

## Layer Responsibilities

| Layer | Purpose | Contains |
|-------|---------|----------|
| **Endpoints** | HTTP handling | Routes, dependency injection |
| **Schemas** | Validation | Pydantic models, validation rules |
| **Services** | Business logic | CRUD, transformations, rules |
| **Models** | Data structure | SQLAlchemy models, relationships |
| **Core** | Infrastructure | Config, DB, logging, exceptions |

## Example: Create Brand

### 1. Schema (schemas/brand.py)
```python
class BrandCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
```

### 2. Service (services/brand_service.py)
```python
class BrandService:
    async def create_brand(self, user_id, data: BrandCreate):
        embedding = generate_embedding(data.name)
        brand = Brand(user_id=user_id, name=data.name, embedding=embedding)
        self.db.add(brand)
        await self.db.commit()
        return brand
```

### 3. Endpoint (api/v1/endpoints/brands.py)
```python
@router.post("", response_model=BrandResponse)
async def create_brand(
    data: BrandCreate,
    service: BrandService = Depends(get_brand_service)
):
    return await service.create_brand(user_id, data)
```

## Dependency Injection

```python
# Service factory
def get_brand_service(db: AsyncSession = Depends(get_db)):
    return BrandService(db)

# Use in endpoint
async def endpoint(service: BrandService = Depends(get_brand_service)):
    return await service.method()
```

## Schema Types

```python
# Base - common fields
class ResourceBase(BaseModel):
    field1: str

# Create - for POST
class ResourceCreate(ResourceBase):
    pass

# Update - for PUT/PATCH (all optional)
class ResourceUpdate(BaseModel):
    field1: Optional[str] = None

# Response - for API output
class ResourceResponse(ResourceBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

## Benefits

✅ Thin controllers (easy to read)  
✅ Reusable services (DRY)  
✅ Type-safe (Pydantic validation)  
✅ Testable (mock services)  
✅ Maintainable (clear separation)  

## Files

- `ARCHITECTURE_REFACTOR.md` - Full refactoring guide
- `schemas/brand.py` - Brand schemas
- `schemas/article.py` - Article schemas
- `services/brand_service.py` - Brand service
- `services/article_service.py` - Article service
- `api/v1/endpoints/brands.py` - Brand endpoints
- `api/v1/endpoints/articles.py` - Article endpoints
