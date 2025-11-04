from pydantic import BaseModel
from typing import Optional, Any

class ErrorResponse(BaseModel):
  message: str
  details: Optional[Any] = None


class Count(BaseModel):
  count: int


class CreateManyTransactions(BaseModel):
  imported: int
  skipped: int
  errors: list[dict]
