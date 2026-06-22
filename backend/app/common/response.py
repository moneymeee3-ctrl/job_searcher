"""EMBEDHUNT AI — Standard API Response Wrapper"""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = ""
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: T = None, message: str = "Success") -> "APIResponse[T]":
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(cls, error: str, message: str = "Request failed") -> "APIResponse":
        return cls(success=False, error=error, message=message)

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool
