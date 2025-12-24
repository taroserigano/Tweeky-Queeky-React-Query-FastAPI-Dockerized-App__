from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Embedded schemas
class ShippingAddressSchema(BaseModel):
    address: str
    city: str
    postal_code: str = Field(alias="postalCode")
    country: str

    class Config:
        populate_by_name = True


class OrderItemSchema(BaseModel):
    name: str
    qty: int
    image: str
    price: float
    product: str

    class Config:
        populate_by_name = True


class PaymentResultSchema(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    update_time: Optional[str] = Field(None, alias="update_time")
    email_address: Optional[str] = Field(None, alias="email_address")

    class Config:
        populate_by_name = True


# Request schemas
class OrderCreate(BaseModel):
    order_items: List[OrderItemSchema] = Field(alias="orderItems")
    shipping_address: ShippingAddressSchema = Field(alias="shippingAddress")
    payment_method: str = Field(alias="paymentMethod")

    class Config:
        populate_by_name = True


class OrderPaymentUpdate(BaseModel):
    id: str
    status: str
    update_time: str
    email_address: str = Field(alias="payer")

    class Config:
        populate_by_name = True


# Response schemas
class OrderResponse(BaseModel):
    id: str = Field(alias="_id")
    user: str
    order_items: List[dict] = Field(alias="orderItems")
    shipping_address: dict = Field(alias="shippingAddress")
    payment_method: str = Field(alias="paymentMethod")
    payment_result: Optional[dict] = Field(None, alias="paymentResult")
    items_price: float = Field(alias="itemsPrice")
    tax_price: float = Field(alias="taxPrice")
    shipping_price: float = Field(alias="shippingPrice")
    total_price: float = Field(alias="totalPrice")
    is_paid: bool = Field(alias="isPaid")
    paid_at: Optional[datetime] = Field(None, alias="paidAt")
    is_delivered: bool = Field(alias="isDelivered")
    delivered_at: Optional[datetime] = Field(None, alias="deliveredAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True
