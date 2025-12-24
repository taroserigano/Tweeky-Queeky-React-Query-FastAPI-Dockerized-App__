from typing import List


def calc_prices(order_items: List[dict]) -> dict:
    """
    Calculate order prices
    
    Args:
        order_items: List of order items with qty and price
        
    Returns:
        dict with itemsPrice, taxPrice, shippingPrice, totalPrice
    """
    # Calculate items price
    items_price = sum(item['price'] * item['qty'] for item in order_items)
    
    # Calculate shipping price (free if over $100, else $10)
    shipping_price = 0 if items_price > 100 else 10
    
    # Calculate tax price (15% tax)
    tax_price = round(0.15 * items_price, 2)
    
    # Calculate total price
    total_price = round(items_price + shipping_price + tax_price, 2)
    
    return {
        "itemsPrice": round(items_price, 2),
        "shippingPrice": round(shipping_price, 2),
        "taxPrice": tax_price,
        "totalPrice": total_price
    }
