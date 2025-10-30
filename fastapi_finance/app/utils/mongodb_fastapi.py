from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class MongoDBFastAPI(FastAPI):
  mongodb_client: AsyncIOMotorClient = None
  mongodb: AsyncIOMotorDatabase = None