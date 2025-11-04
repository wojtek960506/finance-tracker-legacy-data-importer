from app.schema.transaction import (
  TransactionInDB,
  TransactionCreate,
  TransactionFullUpdate,
  TransactionPartialUpdate,
)
from bson import ObjectId
from fastapi import status
from app.api.errors import AppError
from app.db.database import Database
from datetime import datetime, timezone


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


async def update_transaction(
  db: Database,
  id: str,
  transaction: TransactionFullUpdate | TransactionPartialUpdate
):
  doc = transaction.model_dump(
    by_alias=True,
    exclude_none=False,
    exclude_unset=True,
  )
  doc["updatedAt"] = datetime.now(timezone.utc)


  old = await db.transactions.find_one_and_update({ "_id": ObjectId(id)}, { "$set": doc })
  if not old:
    message = f"Transaction with id: '{id}' not found"
    raise AppError(status.HTTP_404_NOT_FOUND, message)

  updated = await db.transactions.find_one({ "_id": old["_id"] })
  return TransactionInDB.model_validate(normalize_id(updated))