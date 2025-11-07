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


class TransactionBase(BaseModel):
  idx: Optional[int] = None
  date: datetime
  description: str
  amount: float
  currency: str
  category: str
  payment_method: str = Field(..., alias="paymentMethod")
  account: str
  exchange_rate: Optional[float] = Field(None, alias="exchangeRate")
  currencies: Optional[str] = None
  calc_ref_idx: Optional[int] = Field(None, alias="calcRefIdx")
  transaction_type: str = Field(..., alias="transactionType")
  created_at: Optional[datetime] = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    alias="createdAt"  
  )
  updated_at: Optional[datetime] = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    alias="updatedAt"
  )

  @field_validator("amount")
  @classmethod
  def amount_must_be_positive(cls, value):
    if value < 0:
      raise PydanticCustomError(
        "amount_less_than_zero",
        "Amount must be greater than zero"
      )
    return value
  
  model_config = ConfigDict(populate_by_name=True)
  

class TransactionCreate(TransactionBase, PartialModelMixin):
  """Schema for creating a new transaction."""
  @model_validator(mode="after")
  def validate_exchange(self):
    """If any of 3 fields is set then all must be set."""
    related = [self.currencies, self.exchange_rate, self.calc_ref_idx]
    provided = [v is not None for v in related]

    if any(provided) and not all(provided):
      raise PydanticCustomError(
        "exchange_group_incomplete",
        "Values for 'currencies', 'exchange_rate' and 'calc_ref_idx' must be provided together"
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
