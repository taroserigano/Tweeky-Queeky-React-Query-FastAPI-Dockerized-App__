"""Helper functions to serialize order nested objects to dictionaries"""


def serialize_order_item(item):
    """Convert OrderItem to dict"""
    return {
        "name": item.name,
        "qty": item.qty,
        "image": item.image,
        "price": item.price,
        "product": str(item.product)
    }


def serialize_shipping_address(address):
    """Convert ShippingAddress to dict"""
    return {
        "address": address.address,
        "city": address.city,
        "postalCode": address.postal_code,
        "country": address.country
    }


def serialize_payment_result(payment):
    """Convert PaymentResult to dict"""
    if not payment:
        return None
    return {
        "id": payment.id,
        "status": payment.status,
        "update_time": payment.update_time,
        "email_address": payment.email_address
    }


def serialize_order(order):
    """Convert Order document to OrderResponse dict"""
    return {
        "_id": str(order.id),
        "user": str(order.user),
        "orderItems": [serialize_order_item(item) for item in order.order_items],
        "shippingAddress": serialize_shipping_address(order.shipping_address),
        "paymentMethod": order.payment_method,
        "paymentResult": serialize_payment_result(order.payment_result),
        "itemsPrice": order.items_price,
        "taxPrice": order.tax_price,
        "shippingPrice": order.shipping_price,
        "totalPrice": order.total_price,
        "isPaid": order.is_paid,
        "paidAt": order.paid_at,
        "isDelivered": order.is_delivered,
        "deliveredAt": order.delivered_at,
        "createdAt": order.created_at,
        "updatedAt": order.updated_at
    }
