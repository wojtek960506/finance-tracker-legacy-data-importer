from fastapi import APIRouter, HTTPException, status, UploadFile, File
from app.schema.transaction import (
  TransactionInDB,
  TransactionCreate,
  TransactionFullUpdate,
  TransactionPartialUpdate
)
from app.utils.mongodb_request import MongoDBRequest
from bson import ObjectId
from datetime import datetime, timezone
import csv
from io import StringIO
import time
from app.decorators import show_execution_time


router = APIRouter()

@router.get("/", response_model=list[TransactionInDB])
@show_execution_time
async def get_transactions(request: MongoDBRequest):
  """Return all transactions from MongoDB."""
  db = request.app.mongodb
  
  raw_transactions = await db.transactions.find().to_list(length=None)

  transactions = []
  for raw_transaction in raw_transactions:
    # Convert ObjectId to string for JSON serialization
    raw_transaction["_id"] = str(raw_transaction["_id"])
    # Convert raw dict to Pydantic model (applies aliases and snake case)
    transaction = TransactionInDB.model_validate(raw_transaction)
    transactions.append(transaction)

  # original column names are returned in response JSON
  # but when calling this function directly it returns Pydantic model objects
  return transactions


@router.get("/count")
@show_execution_time
async def get_transactions_count(request: MongoDBRequest):
  """Return number of all transactions stored in MongoDB."""

  db = request.app.mongodb
  result = await db.transactions.count_documents({})

  return { "count": result }


@router.get("/{id}", response_model=TransactionInDB)
@show_execution_time
async def get_transaction(id: str, request: MongoDBRequest):
  """Return single transaction by id."""
  db = request.app.mongodb

  transaction = await db.transactions.find_one({"_id": ObjectId(id)})
  if not transaction:
    raise HTTPException(
      status.HTTP_404_NOT_FOUND,
      detail=f"Transaction with id: '{id}' not found"
    )
  transaction["_id"] = str(transaction["_id"])
  return TransactionInDB.model_validate(transaction)


@router.post("/", response_model=TransactionInDB, status_code=status.HTTP_201_CREATED)
@show_execution_time
async def create_transaction(request: MongoDBRequest, transaction: TransactionCreate):
  """Create single transaction"""
  db = request.app.mongodb
  result = await db.transactions.insert_one(transaction.model_dump(by_alias=True))

  # get newly created object
  new_transaction = await db.transactions.find_one({ "_id": result.inserted_id })
  new_transaction["_id"] = str(new_transaction["_id"])
  return TransactionInDB.model_validate(new_transaction)


@router.put("/{id}", response_model=TransactionInDB)
@show_execution_time
async def update_transaction_full(
  request: MongoDBRequest,
  id: str,
  transaction: TransactionFullUpdate
):
  """Full update transaction"""
  db = request.app.mongodb
  # exclude defaults and unset not to update value of created at automatically
  doc = transaction.model_dump(by_alias=True, exclude_defaults=True, exclude_unset=True)
  doc["updatedAt"] = datetime.now(timezone.utc)

  print('PUT:', doc)

  old = await db.transactions.find_one_and_update({ "_id": ObjectId(id)}, { "$set": doc })
  if not old:
    raise HTTPException(
      status.HTTP_404_NOT_FOUND,
      detail=f"Transaction with id: '{id}' not found"
    )

  updated = await db.transactions.find_one({ "_id": old["_id"] })
  updated["_id"] = str(updated["_id"])

  return TransactionInDB.model_validate(updated)


@router.patch("/{id}", response_model=TransactionInDB)
@show_execution_time
async def update_transaction_full(
  request: MongoDBRequest,
  id: str,
  transaction: TransactionPartialUpdate
):
  """Partial update of transaction"""
  db = request.app.mongodb
  doc = transaction.model_dump(
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
    exclude_defaults=True
  )
  doc["updatedAt"] = datetime.now(timezone.utc)

  old = await db.transactions.find_one_and_update({ "_id": ObjectId(id)}, { "$set": doc })
  if not old:
    raise HTTPException(
      status.HTTP_404_NOT_FOUND,
      detail=f"Transaction with id: '{id}' not found"
    )

  updated = await db.transactions.find_one({ "_id": old["_id"] })
  updated["_id"] = str(updated["_id"])

  return TransactionInDB.model_validate(updated)


@router.delete("/{id}")
@show_execution_time
async def delete_transaction(request: MongoDBRequest, id: str):
  """Delete single transaction"""
  db = request.app.mongodb
  deleted = await db.transactions.find_one_and_delete({ "_id": ObjectId(id) })

  if not deleted:
    raise HTTPException(
      status.HTTP_404_NOT_FOUND,
      detail=f"Transaction with id: '{id}' not found"
    )

  deleted["_id"] = str(deleted["_id"])
  return TransactionInDB.model_validate(deleted)


@router.delete("/")
@show_execution_time
async def delete_all_transactions(request: MongoDBRequest):
  """Delete single transaction"""
  db = request.app.mongodb
  deleted = await db.transactions.delete_many({})

  return { "deletedCount": deleted.deleted_count }


def normalize_csv_row(row: dict) -> dict:
  normalized_row = {}
  for key, value in row.items():
    if value == '':
      normalized_row[key] = None
    else:
      normalized_row[key] = value
  return normalized_row


@router.post("/import-csv")
@show_execution_time
async def import_transactions_csv(request: MongoDBRequest, file: UploadFile = File(...)):
  """Create transactions based on the data in CSV"""
  if not file.filename.endswith(".csv"):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Only CSV files are supported."
    )
  
  db = request.app.mongodb
  content = await file.read()
  decoded = content.decode("utf-8")
  csv_reader = csv.DictReader(StringIO(decoded))

  valid_docs = []
  errors = []

  for i, row in enumerate(csv_reader, start=1):
    try:
      transaction = TransactionCreate(**normalize_csv_row(row))
      valid_docs.append(transaction.model_dump(by_alias=True))
    except Exception as e:     
      errors.append({ "row": i, "error": str(e) })

  if not valid_docs:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, detail="No valid transactions found in CSV."
    )
  
  inserted_ids = 0

  result = await db.transactions.insert_many(valid_docs)
  inserted_ids = len(result.inserted_ids)
  
  return {
    "imported": inserted_ids,
    "skipped": len(errors),
    "errors": errors[:10]
  }
