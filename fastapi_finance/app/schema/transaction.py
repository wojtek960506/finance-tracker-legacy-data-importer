from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, timezone
from typing import Optional


class TransactionBase(BaseModel):
  idx: Optional[int] = None
  date: datetime
  description: str
  amount: float
  currency: str
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
    if value <= 0:
      raise ValueError("Amount must be greater than zero")
    return value
  
  @model_validator(mode="after")
  def validate_exchange(self):
    """If any of 4 fields is set then all must be set."""
    related = [self.idx, self.currencies, self.exchange_rate, self.calc_ref_idx]
    provided = [v is not None for v in related]

    print(provided)

    if any(provided) and not all(provided):
      raise ValueError(
        "Values for 'idx', 'currencies', 'exchange_rate' and 'calc_ref_idx' must be provided together"
      )
    return self


class TransactionCreate(TransactionBase):
  """Schema for creating a new transaction."""
  pass
  

class TransactionInDB(TransactionBase):
  """Schema for data retrieved from MondoDB"""
  id: str = Field(..., alias="_id")

  class Config:
    populate_by_name = True # allows both _id and id usage
    json_encoders = { datetime: lambda d: d.isoformat() }
