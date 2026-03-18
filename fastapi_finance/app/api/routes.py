from bson import ObjectId
from app.db.database import Database
from app.dependencies.db_dep import get_db
from app.decorators import show_execution_time
from app.api.responses import Count, CreateManyTransactions
from app.services.category_service import create_categories_map
from app.services.csv_service import prepare_transactions_from_csv
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.services.transaction_service import (
  delete_transactions,
  create_transactions,
  serialize_object,
)
from app.services.user_service import find_user
from app.services.transaction_service import count_transactions

router = APIRouter()

@router.delete("/users/{ownerId}", response_model=Count)
@show_execution_time
async def route_delete_transactions(ownerId: str, db: Database = Depends(get_db)):
  """Delete all transactions"""
  deleted_count = await delete_transactions(db, ownerId)
  return { "count": deleted_count }

@router.post("/users/{ownerId}/import-csv", response_model=CreateManyTransactions)
@show_execution_time
async def route_import_transactions_csv(
  owner_id: str,
  db: Database = Depends(get_db),
  file: UploadFile = File(...),
):
  """Create transactions based on the data in CSV"""

  if (await find_user(db, owner_id)) is None:
    raise HTTPException(status_code=404, detail="User not found")

  # do not allow importing transactions' data from CSV for a user who already has transactions
  if (await count_transactions(db, owner_id)) > 0:
    raise HTTPException(
      status_code=409,
      detail="Cannot import transactions for a user who already has some transactions",
    )

  valid_docs, errors = await prepare_transactions_from_csv(file, owner_id)

  categories_map = await create_categories_map(db, owner_id, valid_docs)

  if (errors):
    errors_to_show = list(map(serialize_object, errors[:10]))
    raise HTTPException(
      status_code=400,
      detail={
        "valid_transactions_count": len(valid_docs),
        "invalid_transactions_count": len(errors),
        "first_10_errors": errors_to_show,
      }
    )
  
  return await create_transactions(db, valid_docs, errors, categories_map)
