from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.schema.transaction import (
  TransactionInDB
)
from bson import ObjectId
from fastapi import HTTPException, status

def get_transactions_collection(db: AsyncIOMotorDatabase) -> AsyncIOMotorCollection:
  return db.transactions

async def get_all_transactions(db: AsyncIOMotorDatabase) -> list[TransactionInDB]:

  raw_transactions = await get_transactions_collection(db).find().to_list(length=None)
  transactions = []

  for raw_transaction in raw_transactions:
    # Convert ObjectId to string for JSON serialization
    raw_transaction["_id"] = str(raw_transaction["_id"])
    # Convert raw dict to Pydantic model (applies aliases and snake case)
    transaction = TransactionInDB.model_validate(raw_transaction)
    transactions.append(transaction)

  # original column names are returned when it is used for response in JSON
  # but when calling this function directly it returns Pydantic model objects
  return transactions


async def get_all_transactions_count(db: AsyncIOMotorDatabase) -> int:
  result = await get_transactions_collection(db).count_documents({})
  return result


async def get_transaction(db: AsyncIOMotorDatabase, id: str) -> TransactionInDB:
  transaction = await get_transactions_collection(db).find_one({"_id": ObjectId(id)})

  if not transaction:
    raise HTTPException(
      status.HTTP_404_NOT_FOUND,
      detail=f"Transaction with id: '{id}' not found"
    )
  transaction["_id"] = str(transaction["_id"])
  return TransactionInDB.model_validate(transaction)