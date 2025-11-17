from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderResponse
from app.services.daftra_client import DaftraClient
from app.utils.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=OrderResponse)
async def checkout(  # Changed to async function
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()  # type: ignore

    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    # Validate stock and calculate total
    total_amount = 0
    order_items_data = []

    for cart_item in cart.items:
        product = cart_item.product

        if product.stock < cart_item.quantity:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.title}"
            )

        item_total = product.price * cart_item.quantity  # type: ignore
        total_amount += item_total

        order_items_data.append({
            "product": product,
            "quantity": cart_item.quantity,  # type: ignore
            "price": product.price  # type: ignore
        })

    # Create order
    order = Order(
        user_id=current_user.id,  # type: ignore
        total_amount=total_amount,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items and update stock
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,  # type: ignore
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        db.add(order_item)

        # Update product stock
        current_stock = item_data["product"].stock  # type: ignore
        setattr(item_data["product"], 'stock', current_stock - item_data["quantity"])

    # Clear cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

    # Create invoice in Daftra
    try:
        daftra_client = DaftraClient()
        invoice_data = await daftra_client.prepare_invoice_data(order, current_user, order_items_data)
        daftra_response = await daftra_client.create_invoice(invoice_data)

        # Extract invoice ID from response (adjust based on Daftra API response structure)
        invoice_id = daftra_response.get("id") or daftra_response.get("invoice_id")

        if invoice_id:
            setattr(order, 'daftra_invoice_id', str(invoice_id))  # Fixed: Use setattr
            setattr(order, 'status', "completed")  # Fixed: Use setattr

    except Exception as e:
        # Log the error but don't fail the order creation
        print(f"Daftra invoice creation failed: {str(e)}")
        setattr(order, 'status', "completed")  # Fixed: Use setattr

    db.commit()
    db.refresh(order)

    return order