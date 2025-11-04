from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from app.schema.transaction import (
  TransactionInDB,
  TransactionCreate,
  TransactionFullUpdate,
  TransactionPartialUpdate
)
from app.utils.mongodb_request import MongoDBRequest
import csv
from io import StringIO
from app.decorators import show_execution_time
from app.services.transaction_service import (
  get_all_transactions,
  get_all_transactions_count,
  get_transaction,
  create_transaction,
  update_transaction,
  delete_transaction,
  delete_all_transactions,
)
from app.db.database import Database
from app.dependencies.db_dep import get_db
from app.api.responses import Count


router = APIRouter()

@router.get("/", response_model=list[TransactionInDB])
@show_execution_time
async def route_get_transactions(db: Database = Depends(get_db)):
  """Return all transactions from MongoDB."""
  return await get_all_transactions(db)


@router.get("/count", response_model=Count)
@show_execution_time
async def route_get_transactions_count(db: Database = Depends(get_db)):
  """Return number of all transactions stored in MongoDB."""
  count = await get_all_transactions_count(db)
  return { "count": count }


@router.get("/{id}", response_model=TransactionInDB)
@show_execution_time
async def route_get_transaction(id: str, db: Database = Depends(get_db)):
  """Return single transaction by id."""
  return await get_transaction(db, id)


@router.post("/", response_model=TransactionInDB, status_code=status.HTTP_201_CREATED)
@show_execution_time
async def route_create_transaction(transaction: TransactionCreate, db: Database = Depends(get_db)):
  """Create single transaction"""
  return await create_transaction(db, transaction)


# PUT and PATCH below calls the same method but the validation
# is done based on the type of `transaction` type in definition
@router.put("/{id}", response_model=TransactionInDB)
@show_execution_time
async def route_full_transaction_update(
  id: str,
  transaction: TransactionFullUpdate,
  db: Database = Depends(get_db)
):
  """Full update transaction"""
  await update_transaction(db, id, transaction)
  return await get_transaction(db, id)


@router.patch("/{id}", response_model=TransactionInDB)
@show_execution_time
async def route_partial_transaction_update(
  id: str,
  transaction: TransactionPartialUpdate,
  db: Database = Depends(get_db)
):
  """Partial update of transaction"""
  await update_transaction(db, id, transaction)
  return await get_transaction(db, id)


@router.delete("/{id}")
@show_execution_time
async def route_delete_transaction(id: str, db: Database = Depends(get_db)):
  """Delete single transaction"""
  return await delete_transaction(db, id)


@router.delete("/", response_model=Count)
@show_execution_time
async def route_delete_all_transactions(db: Database = Depends(get_db)):
  """Delete all transactions"""
  deleted_count = await delete_all_transactions(db)
  return { "count": deleted_count }


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
