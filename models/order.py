from beanie import Document, PydanticObjectId
from pydantic import Field, ConfigDict, BaseModel
from datetime import datetime
from typing import List, Optional


class ShippingAddress(BaseModel):
    address: str
    city: str
    postal_code: str = Field(alias="postalCode")
    country: str

    model_config = ConfigDict(populate_by_name=True)


class PaymentResult(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    update_time: Optional[str] = Field(None, alias="update_time")
    email_address: Optional[str] = Field(None, alias="email_address")

    model_config = ConfigDict(populate_by_name=True)


class OrderItem(BaseModel):
    name: str
    qty: int
    image: str
    price: float
    product: PydanticObjectId

    model_config = ConfigDict(populate_by_name=True)


class Order(Document):
    user: PydanticObjectId
    order_items: List[OrderItem] = Field(alias="orderItems")
    shipping_address: ShippingAddress = Field(alias="shippingAddress")
    payment_method: str = Field(alias="paymentMethod")
    payment_result: Optional[PaymentResult] = Field(None, alias="paymentResult")
    items_price: float = Field(default=0.0, alias="itemsPrice")
    tax_price: float = Field(default=0.0, alias="taxPrice")
    shipping_price: float = Field(default=0.0, alias="shippingPrice")
    total_price: float = Field(default=0.0, alias="totalPrice")
    is_paid: bool = Field(default=False, alias="isPaid")
    paid_at: Optional[datetime] = Field(None, alias="paidAt")
    is_delivered: bool = Field(default=False, alias="isDelivered")
    delivered_at: Optional[datetime] = Field(None, alias="deliveredAt")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)

    class Settings:
        name = "orders"
        use_state_management = True

    async def save(self, *args, **kwargs):
        """Update timestamp on save"""
        self.updated_at = datetime.utcnow()
        return await super().save(*args, **kwargs)
