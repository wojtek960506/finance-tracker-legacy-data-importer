from fastapi import APIRouter
from app.schema.transaction import TransactionInDB
from app.utils.mongodb_request import MongoDBRequest


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
