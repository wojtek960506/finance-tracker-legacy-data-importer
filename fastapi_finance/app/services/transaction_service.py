from app.schema.transaction import (
  TransactionInDB,
  TransactionCreate,
)
from bson import ObjectId
from fastapi import status
from app.api.errors import AppError
from app.db.database import Database

def normalize_id(transaction):
  transaction["_id"] = str(transaction["_id"])
  return transaction


async def get_all_transactions(db: Database) -> list[TransactionInDB]:
  transactions = await db.transactions.find().to_list(length=None)
  return [TransactionInDB.model_validate(normalize_id(t)) for t in transactions]


async def get_all_transactions_count(db: Database) -> int:
  return await db.transactions.count_documents({})


async def get_transaction(db: Database, id: str) -> TransactionInDB:
  transaction = await db.transactions.find_one({"_id": ObjectId(id)})
  if not transaction:
    raise AppError(
      status_code=status.HTTP_404_NOT_FOUND,
      message=f"Transaction with id: '{id}' not found"
    )
  return TransactionInDB.model_validate(normalize_id(transaction))


async def create_transaction(db: Database, transaction: TransactionCreate):
  result = await db.transactions.insert_one(transaction.model_dump(by_alias=True))
  # get newly created object
  new_t = await db.transactions.find_one({ "_id": result.inserted_id })
  return TransactionInDB.model_validate(normalize_id(new_t))