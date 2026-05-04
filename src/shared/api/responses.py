from pydantic import BaseModel
from typing import Optional, Any, TypedDict

class ErrorResponse(BaseModel):
  message: str
  details: Optional[Any] = None


class Count(BaseModel):
  count: int


class CreateManyTransactions(TypedDict):
  imported: int
  skipped: int
  errors: list[dict]
  updateErrors: list[dict]
