from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ProductCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=255)
    description: str = ""
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)

class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class StockUpdate(BaseModel):
    quantity: int = Field(ge=0)
