from fastapi import APIRouter, status, UploadFile, File, Depends
from app.schema.transaction import (
  TransactionInDB,
  TransactionCreate,
  TransactionFullUpdate,
  TransactionPartialUpdate
)
from app.decorators import show_execution_time
from app.services.transaction_service import (
  get_all_transactions,
  get_all_transactions_count,
  get_transaction,
  create_transaction,
  update_transaction,
  delete_transaction,
  delete_all_transactions,
  create_many_transactions,
)
from app.services.csv_service import prepare_transactions_from_csv
from app.db.database import Database
from app.dependencies.db_dep import get_db
from app.api.responses import Count, CreateManyTransactions


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


@router.post("/import-csv", response_model=CreateManyTransactions)
@show_execution_time
async def route_import_transactions_csv(
  db: Database = Depends(get_db), file: UploadFile = File(...)
):
  """Create transactions based on the data in CSV"""
  valid_docs, errors = await prepare_transactions_from_csv(file)
  return await create_many_transactions(db, valid_docs, errors)
