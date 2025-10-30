from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router as api_router, get_transactions
from app.services.db import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
  # --- Startup ---
  await init_db(app)

  yield # app runs here

  # --- Shutdown ---
  close_db(app)


app = FastAPI(title="Finance API", lifespan=lifespan)

# Register routes
app.include_router(api_router, prefix="/api/transactions")
