"""Pydantic schemas for Product CRUD operations."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., max_length=255, examples=["Xarelto"])
    active_substance: str = Field(..., max_length=255, examples=["Rivaroxaban"])
    mah: str = Field(..., max_length=255, examples=["Bayer AG"])
    ibd: date = Field(..., description="International Birth Date")
    status: str = Field(default="Active", max_length=50)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    active_substance: str | None = None
    mah: str | None = None
    ibd: date | None = None
    status: str | None = None


class ProductRead(ProductBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductList(BaseModel):
    items: list[ProductRead]
    total: int
