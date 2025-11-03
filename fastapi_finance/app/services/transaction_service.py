from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.schema.transaction import (
  TransactionInDB
)

def get_transactions_collection(db: AsyncIOMotorDatabase) -> AsyncIOMotorCollection:
  return db.transactions

async def get_all_transactions(db: AsyncIOMotorDatabase):

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
