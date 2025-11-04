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
from app.api.responses import CreateManyTransactions
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
  """Update transaction. In case of no transaction with given `id`, error is thrown. Otherwise
  full object of deleted transaction is returned."""
  doc = transaction.model_dump(
    by_alias=True,
    exclude_none=False,
    exclude_unset=True,
  )
  doc["updatedAt"] = datetime.now(timezone.utc)

  old = await db.transactions.find_one_and_update({ "_id": ObjectId(id)}, { "$set": doc })
  if not old:
    message = f"Transaction with id: '{id}' not found, so not updated"
    raise AppError(status.HTTP_404_NOT_FOUND, message)
  return old


async def delete_transaction(db: Database, id: str) -> TransactionInDB:
  """Delete transaction. In case of no transaction with given `id`, error is thrown."""
  deleted = await db.transactions.find_one_and_delete({ "_id": ObjectId(id) })

  if not deleted:
    message = f"Transaction with id: '{id}' not found, so not deleted" 
    raise AppError(status.HTTP_404_NOT_FOUND, message)

  deleted["_id"] = str(deleted["_id"])
  return TransactionInDB.model_validate(deleted)


# for testing purposes - later some authorization only for admin will be added
async def delete_all_transactions(db: Database) -> int:
  result = await db.transactions.delete_many({})
  return result.deleted_count


async def create_many_transactions(
    db: Database,
    transactions: list[TransactionCreate],
    errors: list[dict]
  ) -> CreateManyTransactions:
  result = await db.transactions.insert_many(transactions)
  return {
    "imported": len(result.inserted_ids),
    "skipped": len(errors),
    "errors": errors[:10]
  }

