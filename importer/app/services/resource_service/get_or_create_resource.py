from app.db.database import Database
from .create_resource import create_resource

from .get_resource_by_name import get_resource_by_name
from .resource_enum import ResourceEnum

async def get_or_create_resource(
    resource_enum: ResourceEnum,
    db: Database,
    name: str,
    owner_id: str,
    should_print: bool = False,
):
  resource = await get_resource_by_name(resource_enum, db, name, owner_id)

  if resource is None:
    resource = await create_resource(resource_enum, db, name, owner_id, should_print)

  if should_print:
    print(f"found or created {resource_enum.field_name}:", resource)

  return resource
