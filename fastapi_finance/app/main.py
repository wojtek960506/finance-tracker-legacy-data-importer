from contextlib import asynccontextmanager
from app.api.routes import router as api_router
from app.db.client import init_db, close_db
from app.utils.mongodb_fastapi import MongoDBFastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.errors import (
  AppError, 
  app_error_handler,
  http_error_handler,
  validation_error_handler
)

@asynccontextmanager
async def lifespan(app: MongoDBFastAPI):
  # --- Startup ---
  await init_db(app)

  yield # app runs here

  # --- Shutdown ---
  close_db(app)


app = MongoDBFastAPI(title="Finance API", lifespan=lifespan)

# Register global exception handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)

# Register routes
app.include_router(api_router, prefix="/api/transactions")
