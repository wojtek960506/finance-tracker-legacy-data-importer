import re
from bson import ObjectId
from fastapi import HTTPException
from app.db.database import Database
from app.schema.transaction import TransactionCreate


def normalize_whitespace(s: str) -> str:
  return re.sub(r"\s+", " ", s).strip()


async def get_category_by_name(db: Database, name: str, owner_id: str):
  return await db.categories.find_one({
    "nameNormalized": normalize_whitespace(name).lower(),
    "$or": [
      { "type": "user", "ownerId": owner_id },
      { "type": "system", "ownerId": None },
    ]
  })


async def create_category(db: Database, name: str, owner_id: str):
  if owner_id is None:
    raise HTTPException(
      status_code=400,
      detail="You can only create user category so owner has to be specified"
    )
  
  doc = {
    "ownerId": ObjectId(owner_id),
    "type": "user",
    "name": normalize_whitespace(name),
    "nameNormalized": normalize_whitespace(name).lower(),
  }
  result = await db.categories.insert_one(doc)

  print("inserted category result", result)

  doc_with_id = dict(doc)
  doc_with_id["_id"] = result.inserted_id
  return doc_with_id


async def get_or_create_category(db, name: str, owner_id: str):
  category = await get_category_by_name(db, name, owner_id)

  if category is None:
    category = await create_category(db, name, owner_id)

  print("found or created category", category)

  return category
  

async def create_categories_map(
  db: Database,
  owner_id: str,
  transactions: list[TransactionCreate],
) -> dict[str, ObjectId]:
  
  categories = set()

  for transaction in transactions:
    categories.add(transaction["category"])

  categories_map = {}

  for category_name in categories:
    category = await get_or_create_category(db, category_name, owner_id)
    if category is None:
      print(f"category {category_name} not found")
      continue

    categories_map[category_name] = category["_id"]

  return categories_map
