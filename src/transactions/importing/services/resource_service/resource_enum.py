from enum import Enum
from typing import Literal

ResourceCollectionName = Literal["categories", "accounts", "paymentmethods"]
ResourceFieldName  = Literal["category", "account", "payment_method"]

class ResourceEnum(str, Enum):
  field_name: ResourceFieldName
  collection_name: ResourceCollectionName
  
  ACCOUNT = ("account", "accounts")
  CATEGORY = ("category", "categories")
  PAYMENT_METHOD = ("payment_method", "paymentmethods")

  def __new__(cls, field_name: ResourceFieldName, collection_name: ResourceCollectionName):
    obj = str.__new__(cls, collection_name)
    obj._value_ = collection_name
    obj.field_name = field_name
    obj.collection_name = collection_name
    return obj
  