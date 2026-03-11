from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


# Association table for many-to-many relationship
note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Relationships
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="notes")


class ActionItem(Base, TimestampMixin):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(7), nullable=True)  # Hex color code
    
    # Relationships
    notes = relationship("Note", secondary=note_tags, back_populates="tags")


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    notes = relationship("Note", back_populates="category")
