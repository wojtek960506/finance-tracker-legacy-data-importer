import csv
from bson import ObjectId
from io import StringIO
from fastapi import UploadFile, status
from app.api.errors import AppError
from app.schema.transaction import TransactionCreate
from pydantic_core import ValidationError


def normalize_csv_row(row: dict) -> dict:
  normalized_row = {}
  for key, value in row.items():
    if value == '':
      normalized_row[key] = None
    else:
      normalized_row[key] = value
  return normalized_row


def prepare_transactions_from_csv_text(
  csv_text: str,
  id: str,
) -> tuple[list[TransactionCreate], list[dict]]:
  csv_reader = csv.DictReader(StringIO(csv_text))

  valid_docs = []
  errors = []

  for i, row in enumerate(csv_reader, start=1):
    try:
      transaction = TransactionCreate(
        **normalize_csv_row(row),
        ownerId=ObjectId(id)
      )
      valid_docs.append(transaction.model_dump(by_alias=True))
    except ValidationError as e:
      errors.append({ "row": i, "error": e.errors() })

  if not valid_docs:
    raise AppError(status.HTTP_400_BAD_REQUEST, "No valid transactions found in CSV.")

  return valid_docs, errors


def prepare_transactions_from_csv_path(
  csv_path: str,
  id: str,
) -> tuple[list[TransactionCreate], list[dict]]:
  if not csv_path.endswith(".csv"):
    raise AppError(status.HTTP_400_BAD_REQUEST, "Only CSV files are supported.")

  with open(csv_path, encoding="utf-8") as csv_file:
    csv_text = csv_file.read()

  return prepare_transactions_from_csv_text(csv_text, id)


async def prepare_transactions_from_csv(
    file: UploadFile,
    id: str,
  ) -> tuple[list[TransactionCreate], list[dict]]:
  if not file.filename.endswith(".csv"):
    raise AppError(status.HTTP_400_BAD_REQUEST, "Only CSV files are supported.")
  
  content = await file.read()
  decoded = content.decode("utf-8")
  return prepare_transactions_from_csv_text(decoded, id)
