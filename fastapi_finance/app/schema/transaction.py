from pydantic import (
  BaseModel,
  Field,
  field_validator,
  model_validator,
  ConfigDict,
  field_serializer
)
from pydantic_partial import PartialModelMixin
from pydantic_core import PydanticCustomError
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId


class TransactionBase(BaseModel):
  date: datetime
  description: str
  amount: float
  currency: str
  category: str
  payment_method: str = Field(..., alias="paymentMethod")
  account: str
  exchange_rate: Optional[float] = Field(None, alias="exchangeRate")
  currencies: Optional[str] = None
  transaction_type: str = Field(..., alias="transactionType")
  created_at: Optional[datetime] = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    alias="createdAt"  
  )
  updated_at: Optional[datetime] = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    alias="updatedAt"
  )
  ownerId: ObjectId
  source_index: int = Field(..., alias="sourceIndex")
  source_ref_index: Optional[int] = Field(None, alias="sourceRefIndex")


  @field_validator("amount")
  @classmethod
  def amount_must_be_positive(cls, value):
    if value < 0:
      raise PydanticCustomError(
        "amount_less_than_zero",
        "Amount must be greater than zero"
      )
    return value
  
  model_config = ConfigDict(
    populate_by_name=True,
    json_encoders={ ObjectId: str },
    arbitrary_types_allowed=True
  )
  

class TransactionCreate(TransactionBase, PartialModelMixin):
  """Schema for creating a new transaction."""
  @model_validator(mode="after")
  def validate_other_currency_transaction(self):

    if (self.category == "exchange"):
      # when type is exchange then we need all 3 fields together
      related = [self.currencies, self.exchange_rate, self.source_ref_index]
      provided = [v is not None for v in related]

      if any(provided) and not all(provided):
        raise PydanticCustomError(
          "exchange_group_incomplete",
          "Values for 'currencies', 'exchange_rate' and 'source_ref_index' must be provided together"
        )
    
    else:
      # when type is not exchange and we have some other currency fields
      # then they have to be together
      related = [self.currencies, self.exchange_rate]
      provided = [v is not None for v in related]

      if any(provided) and not all(provided):
        raise PydanticCustomError(
          "other_currency_group_incomplete",
          "Values for 'currencies' and 'exchange_rate' must be provided together"
          " when any of them is specified for foreign transaction"
        )

    return self
  pass

class TransactionFullUpdate(TransactionCreate):
  """Schema for full update of transaction."""
  pass

TransactionPartialUpdateBase = TransactionCreate.model_as_partial()

class TransactionPartialUpdate(TransactionPartialUpdateBase):
  """Schema for partial update of transaction."""
  pass

class TransactionInDB(TransactionBase):
  """Schema for data retrieved from MondoDB"""
  id: str = Field(..., alias="_id")

  model_config = ConfigDict(populate_by_name = True)

  @field_serializer("date", "created_at", "updated_at", when_used="json")
  def serialize_datetimes(self, value: datetime) -> str:
    return value.isoformat()
