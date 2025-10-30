from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TransactionBase(BaseModel):
  idx: Optional[int] = None
  date: datetime
  description: str
  amount: float
  currency: str
  payment_method: str = Field(..., alias="paymentMethod")
  account: str
  exchange_rate: Optional[float] = None
  currencies: Optional[str] = None
  calc_ref_idx: Optional[int] = None
  transaction_type: str = Field(..., alias="transactionType")


class TransactionInDB(TransactionBase):
  """Schema for data retrieved from MondoDB"""
  id: str = Field(..., alias="_id")

  class Config:
    populate_by_name = True # allows both _id and id usage
    json_encoders = { datetime: lambda d: d.isoformat() }
