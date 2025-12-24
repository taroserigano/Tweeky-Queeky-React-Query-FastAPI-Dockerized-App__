from fastapi import APIRouter, Depends, HTTPException, status
from models.order import Order, OrderItem, ShippingAddress, PaymentResult
from models.product import Product
from models.user import User
from schemas.order import OrderCreate, OrderPaymentUpdate, OrderResponse
from middleware.auth import get_current_user, require_admin
from utils.calc_prices import calc_prices
from utils.paypal import verify_paypal_payment, check_if_new_transaction
from utils.order_serializer import serialize_order
from typing import List
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_order_items(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new order"""
    if not order_data.order_items or len(order_data.order_items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No order items"
        )
    
    # Get ordered items from database to verify prices
    item_ids = [ObjectId(item.product) for item in order_data.order_items]
    items_from_db = await Product.find({"_id": {"$in": item_ids}}).to_list()
    
    # Create a map for quick lookup
    db_items_map = {str(item.id): item for item in items_from_db}
    
    # Map order items with correct prices from database
    db_order_items = []
    for item_from_client in order_data.order_items:
        matching_item = db_items_map.get(item_from_client.product)
        if not matching_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item_from_client.product} not found"
            )
        
        db_order_items.append({
            "name": item_from_client.name,
            "qty": item_from_client.qty,
            "image": item_from_client.image,
            "price": matching_item.price,  # Use price from DB
            "product": ObjectId(item_from_client.product)
        })
    
    # Calculate prices
    prices = calc_prices(db_order_items)
    
    # Convert dict items to OrderItem objects
    order_items_objects = [
        OrderItem(
            name=item["name"],
            qty=item["qty"],
            image=item["image"],
            price=item["price"],
            product=item["product"]
        )
        for item in db_order_items
    ]
    
    # Create order
    order = Order(
        order_items=order_items_objects,
        user=current_user.id,
        shipping_address=ShippingAddress(
            address=order_data.shipping_address.address,
            city=order_data.shipping_address.city,
            postal_code=order_data.shipping_address.postal_code,
            country=order_data.shipping_address.country
        ),
        payment_method=order_data.payment_method,
        items_price=prices["itemsPrice"],
        tax_price=prices["taxPrice"],
        shipping_price=prices["shippingPrice"],
        total_price=prices["totalPrice"]
    )
    
    await order.save()
    
    # Return the serialized order directly (frontend expects direct order object)
    return serialize_order(order)


@router.get("/mine", response_model=List[OrderResponse])
async def get_my_orders(current_user: User = Depends(get_current_user)):
    """Get logged in user orders"""
    orders = await Order.find(Order.user == current_user.id).to_list()
    
    return [OrderResponse(**serialize_order(order)) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get order by ID"""
    try:
        order = await Order.get(ObjectId(order_id))
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return OrderResponse(**serialize_order(order))


@router.put("/{order_id}/pay", response_model=OrderResponse)
async def update_order_to_paid(
    order_id: str,
    payment_data: OrderPaymentUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update order to paid"""
    # Verify the payment was made to PayPal
    payment_info = await verify_paypal_payment(payment_data.id)
    
    if not payment_info["verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment not verified"
        )
    
    # Check if this transaction has been used before
    is_new = await check_if_new_transaction(Order, payment_data.id)
    
    if not is_new:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction has been used before"
        )
    
    try:
        order = await Order.get(ObjectId(order_id))
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check correct amount was paid
    paid_correct_amount = str(order.total_price) == payment_info["value"]
    
    if not paid_correct_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect amount paid"
        )
    
    order.is_paid = True
    order.paid_at = datetime.utcnow()
    order.payment_result = PaymentResult(
        id=payment_data.id,
        status=payment_data.status,
        update_time=payment_data.update_time,
        email_address=payment_data.email_address
    )
    
    await order.save()
    
    return OrderResponse(**serialize_order(order))


@router.put("/{order_id}/deliver", response_model=OrderResponse)
async def update_order_to_delivered(
    order_id: str,
    admin_user: User = Depends(require_admin)
):
    """Update order to delivered (Admin only)"""
    try:
        order = await Order.get(ObjectId(order_id))
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.is_delivered = True
    order.delivered_at = datetime.utcnow()
    
    await order.save()
    
    return OrderResponse(**serialize_order(order))


@router.get("", response_model=List[OrderResponse])
async def get_orders(admin_user: User = Depends(require_admin)):
    """Get all orders (Admin only)"""
    orders = await Order.find_all().to_list()
    
    return [OrderResponse(**serialize_order(order)) for order in orders]
