from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Category, Tag
from ..schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    TagCreate,
    TagRead,
    TagUpdate,
)

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)) -> list[TagRead]:
    rows = db.execute(select(Tag)).scalars().all()
    return [TagRead.model_validate(row) for row in rows]


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    # Check if tag already exists
    existing = db.execute(select(Tag).where(Tag.name == payload.name)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    tag = Tag(name=payload.name, color=payload.color)
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return TagRead.model_validate(tag)


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, db: Session = Depends(get_db)) -> TagRead:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagRead.model_validate(tag)


@router.patch("/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, payload: TagUpdate, db: Session = Depends(get_db)) -> TagRead:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    if payload.name is not None:
        # Check if name already exists
        existing = db.execute(
            select(Tag).where(Tag.name == payload.name, Tag.id != tag_id)
        ).scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="Tag name already exists")
        tag.name = payload.name
    
    if payload.color is not None:
        tag.color = payload.color
    
    db.flush()
    db.refresh(tag)
    return TagRead.model_validate(tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.flush()


# Category router
cat_router = APIRouter(prefix="/categories", tags=["categories"])


@cat_router.get("/", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryRead]:
    rows = db.execute(select(Category)).scalars().all()
    return [CategoryRead.model_validate(row) for row in rows]


@cat_router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> CategoryRead:
    existing = db.execute(select(Category).where(Category.name == payload.name)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    category = Category(name=payload.name, description=payload.description)
    db.add(category)
    db.flush()
    db.refresh(category)
    return CategoryRead.model_validate(category)


@cat_router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryRead:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryRead.model_validate(category)


@cat_router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)) -> CategoryRead:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if payload.name is not None:
        existing = db.execute(
            select(Category).where(Category.name == payload.name, Category.id != category_id)
        ).scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")
        category.name = payload.name
    
    if payload.description is not None:
        category.description = payload.description
    
    db.flush()
    db.refresh(category)
    return CategoryRead.model_validate(category)


@cat_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.flush()
