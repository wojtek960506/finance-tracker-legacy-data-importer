import json

from src.shared.db.client import database_session
from src.shared.utils import print_table

from .list_users_utils import (
  count_user_resources,
  serialize_user,
  serialize_value,
)


async def run_users_list(include_raw: bool, as_json: bool) -> int:
  async with database_session() as db:
    users = await db.users.find({}).sort("_id", 1).to_list(length=None)
    result = []

    print(f"Calculating transaction and resource counts for {len(users)} users...")

    for user in users:
      transactions_count = await db.transactions.count_documents({
        "ownerId": user["_id"]
      })
      resources_count = await count_user_resources(db, user["_id"])
      counts = {
        "transactions": transactions_count,
        **resources_count,
      }

      if include_raw:
        serialized_user = serialize_value(user)
        serialized_user.update(counts)
        result.append(serialized_user)
      else:
        result.append(serialize_user(user, counts))

    if include_raw or as_json:
      print(json.dumps(result, indent=2, default=str))
    else:
      print_table(result)

    return 0
