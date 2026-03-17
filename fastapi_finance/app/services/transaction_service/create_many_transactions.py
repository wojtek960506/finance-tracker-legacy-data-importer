from app.schema.transaction import TransactionCreate
from bson import ObjectId
from app.db.database import Database
from app.api.responses import CreateManyTransactions
from pymongo import UpdateOne
from .serialize_object import serialize_object

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

  errors_to_show = list(map(serialize_object, errors[:10]))

  # when we have some errors and there is an ObjectId there as bson, then the Internal
  # Server error is thrown, because serializer is not able to serialize it
  return {
    "imported": len(result.inserted_ids),
    "skipped": len(errors),
    "errors": errors_to_show,
    "updateErrors": update_errors,
  }