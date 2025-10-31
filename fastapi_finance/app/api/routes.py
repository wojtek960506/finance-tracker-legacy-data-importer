from fastapi import APIRouter, HTTPException, status
from app.schema.transaction import TransactionInDB, TransactionCreate, TransactionFullUpdate
from app.utils.mongodb_request import MongoDBRequest
from bson import ObjectId


router = APIRouter()

@router.get("/", response_model=list[TransactionInDB])
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

@router.get("/{id}", response_model=TransactionInDB)
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
async def create_transaction(request: MongoDBRequest, transaction: TransactionCreate):
  """Create single transaction"""
  db = request.app.mongodb
  result = await db.transaction.insert_one(transaction.model_dump(by_alias=True))

  # get newly created object
  new_transaction = await db.transaction.find_one({ "_id": result.inserted_id })
  new_transaction["_id"] = str(new_transaction["_id"])
  return TransactionInDB.model_validate(new_transaction)

@router.put("/{id}", response_model=TransactionInDB)
async def update_transaction_full(
  request: MongoDBRequest,
  id: str,
  transaction: TransactionFullUpdate
):
  """Update whole transaction"""
  db = request.app.mongodb
  udpated = await db.transactions.find_one_and_update(
    { "_id": ObjectId(id)},
    { "$set": transaction.model_dump(by_alias=True) }
  )

  if not udpated:
    raise HTTPException(
      status.HTTP_404_NOT_FOUND,
      detail=f"Transaction with id: '{id}' not found"
    )

  udpated["_id"] = str(udpated["_id"])
  return TransactionInDB.model_validate(udpated)

@router.delete("/{id}")
async def delete_transaction(request: MongoDBRequest, id: str):
  """Delete single transaction"""
  db = request.app.mongodb
  deleted = await db.transaction.find_one_and_delete({ "_id": ObjectId(id) })

  if not deleted:
    raise HTTPException(
      status.HTTP_404_NOT_FOUND,
      detail=f"Transaction with id: '{id}' not found"
    )

  deleted["_id"] = str(deleted["_id"])
  return TransactionInDB.model_validate(deleted)


