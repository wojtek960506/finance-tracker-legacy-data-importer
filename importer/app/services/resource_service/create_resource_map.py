from bson import ObjectId
from app.db.database import Database
from app.schema.transaction import TransactionCreate
from app.services.resource_service.resource_enum import ResourceEnum
from .get_or_create_resource import get_or_create_resource


async def create_resource_map(
  resource_enum: ResourceEnum,
  db: Database,
  owner_id: str,
  transactions: list[TransactionCreate],
  should_print: bool = False,
) -> dict[str, ObjectId]:
  
  resources = set()
  for transaction in transactions:
    resources.add(getattr(transaction, resource_enum.field_name))

  resource_map = {}
  for resource_name in resources:
    resource = await get_or_create_resource(
      resource_enum, db, resource_name, owner_id, should_print
    )
    if resource is None:
      if should_print:
        print(f"{resource_enum.field_name} {resource_name} not found")
      continue

    resource_map[resource_name] = resource["_id"]

  return resource_map
