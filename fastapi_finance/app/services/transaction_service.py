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
from pymongo import UpdateOne


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


def serialize_object_id_if_any(obj):
  # owner id has to be serialized to string because when it is passed as bson.ObjectId,
  # then such error is thrown: "pydantic_core._pydantic_core.PydanticSerializationError:
  # Unable to serialize unknown type: <class 'bson.objectid.ObjectId'>""

  error = obj.get('error')
  if error is None:
    print('isNone')
    return obj

  new_error_arr = []

  for e in error:
    input_dict = e.get("input")
    if input_dict is None:
      new_error_arr.append(e)
    else:
      input_dict = dict(input_dict)
      ownerId = input_dict.get('ownerId')
      if ownerId is None:
        new_error_arr.append(e)
      else:
        input_dict['ownerId'] = str(input_dict['ownerId'])
        e['input'] = input_dict
        new_error_arr.append(e)

  obj['error'] = new_error_arr
  return obj

async def create_many_transactions(
    db: Database,
    transactions: list[TransactionCreate],
    errors: list[dict],
    categories_map: dict[str, ObjectId],
  ) -> CreateManyTransactions:


  # TODO - think about other schema of return value
  #        as errors are handled before calling this function
  if len(transactions) == 0:
    return {
      "imported": 0,
      "skipped": 0,
      "errors": [],
      "updateErrors": [],
    }
  
  for transaction in transactions:
    transaction["categoryId"] = categories_map[transaction.pop("category")]

  result = await db.transactions.insert_many(transactions)

  # ##################################################################
  # UPDATE TRANSACTIONS WITH REFERENCES AS `_id` VALUES FROM DB
  n_source_index = "sourceIndex"
  n_source_ref_index = "sourceRefIndex"

  real_idx_to_id = {
    t[n_source_index]: result.inserted_ids[i]
    for i,t in enumerate(transactions)
  }

  # prepare bulk updates
  updates = []
  update_errors = []

  for t in transactions:
    ref = t.get(n_source_ref_index)
    if not ref:
      continue

    try:
      updates.append(
        UpdateOne(
          {"_id": real_idx_to_id[t[n_source_index]]},
          {"$set": {"refId": real_idx_to_id[ref]}}
        )
      )
    except KeyError as err:
      update_errors.append({
        "sourceIndex": t[n_source_index],
        "error": f"Broken 'sourceRefIndex' - {str(err)}"
      })

  # execute updates
  if updates:
    await db.transactions.bulk_write(updates)
  # ##################################################################

  # ------------------------------------------------------------------
  # store the max `source_index` to properly add new transaction
  owner_id = transactions[0]["ownerId"]
  max_source_index = await db.transactions.find_one(
    { "ownerId": owner_id },
    sort=[("sourceIndex", -1)],
    projection={"sourceIndex": 1}
  )
  start = max_source_index["sourceIndex"] if max_source_index else 0
  await db.counters.update_one(
    {"_id": {"type": "transactions", "userId": owner_id}},
    {"$set": {"seq": start}},
    upsert=True
  )
  # ------------------------------------------------------------------

  errors_to_show = list(map(serialize_object_id_if_any, errors[:10]))

  # when we have some errors and there is an ObjectId there as bson, then the Internal
  # Server error is thrown, because serializer is not able to serialize it
  return {
    "imported": len(result.inserted_ids),
    "skipped": len(errors),
    "errors": errors_to_show,
    "updateErrors": update_errors,
  }

