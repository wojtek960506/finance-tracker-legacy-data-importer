from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.db.database import Database

class MongoDBFastAPI(FastAPI):
  mongodb_client: AsyncIOMotorClient = None
  mongodb: AsyncIOMotorDatabase = None
  db: Database = None
