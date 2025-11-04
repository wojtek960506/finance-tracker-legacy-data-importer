from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .responses import ErrorResponse


class AppError(Exception):
  """Base class for application-level errors."""
  def __init__(self, status_code: int, message: str, details=None):
    self._status_code = status_code
    self._message = message
    self._details = details

  @property
  def status_code(self):
    return self._status_code
  
  @property
  def message(self):
    return self._message
  
  @property
  def details(self):
    return self._details


async def app_error_handler(_: Request, exc: AppError):
  return JSONResponse(
    status_code=exc.status_code,
    content=ErrorResponse(message=exc.message, details=exc.details).model_dump()
  )


async def validation_error_handler(_: Request, exc: RequestValidationError):
  return JSONResponse(
    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    content=ErrorResponse(
      message="Validation failed",
      details=exc.errors()
    ).model_dump()
  )


async def http_error_handler(_: Request, exc: StarletteHTTPException):
  return JSONResponse(
    status_code=exc.status_code,
    content=ErrorResponse(message=exc.detail or "HTTP Error", details=exc.detail).model_dump()
  )




