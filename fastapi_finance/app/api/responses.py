from pydantic import BaseModel
from typing import Optional, Any

class ErrorResponse(BaseModel):
  message: str
  details: Optional[Any] = None
