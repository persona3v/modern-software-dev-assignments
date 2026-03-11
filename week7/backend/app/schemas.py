from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=10000)
    tag_ids: list[int] = []
    category_id: int | None = None

    @field_validator('title', 'content', mode='before')
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    tags: list["TagRead"] = []
    category: "CategoryRead" | None = None

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = None
    content: str | None = None
    tag_ids: list[int] = []
    category_id: int | None = None


class ActionItemCreate(BaseModel):
    description: str


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = None
    completed: bool | None = None


# New schemas for Tag and Category
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str | None = None


class TagRead(BaseModel):
    id: int
    name: str
    color: str | None = None

    class Config:
        from_attributes = True


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


