from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router as api_router
from app.services.db import init_db, close_db
from app.utils.mongodb_fastapi import MongoDBFastAPI

@asynccontextmanager
async def lifespan(app: MongoDBFastAPI):
  # --- Startup ---
  await init_db(app)

  yield # app runs here

  # --- Shutdown ---
  close_db(app)


app = MongoDBFastAPI(title="Finance API", lifespan=lifespan)

# Register routes
app.include_router(api_router, prefix="/api/transactions")
