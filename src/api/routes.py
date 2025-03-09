from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import Product, Order
from api.worker import process_order, send_order_confirmation
from pydantic import BaseModel
from api.telemetry import get_tracer
import logging

router = APIRouter()

# Logging
logger = logging.getLogger(__name__)

# Get a tracer
tracer = get_tracer(__name__)

# Product Schema
class ProductCreate(BaseModel):
    name: str
    price: float

# Order Schema
class OrderCreate(BaseModel):
    product_id: int
    quantity: int

@router.get("/products")
def get_products(db: Session = Depends(get_db)):
    with get_tracer(__name__).start_as_current_span("get_products"):
        products = db.query(Product).all()
        return products

@router.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    with get_tracer(__name__).start_as_current_span("create_product"):
        db_product = Product(name=product.name, price=product.price)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Product created: {db_product.name} (${db_product.price})")
        return db_product

@router.post("/checkout")
def checkout(order: OrderCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("checkout_order"):
        # Verify product exists
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Create order record in database
        db_order = Order(product_id=order.product_id, quantity=order.quantity)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Send to Celery for background processing
        order_data = {"product_id": order.product_id, "quantity": order.quantity}
        task = process_order.delay(order_data)
        
        # Queue confirmation email
        background_tasks.add_task(send_order_confirmation.delay, db_order.id)

        logger.info(f"Order placed: Product {order.product_id} x{order.quantity}, Task ID: {task.id}")
        return {
            "message": "Order received, processing in the background",
            "order_id": db_order.id,
            "task_id": task.id
        }

@router.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@router.post("/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Verify product exists
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Create order record in database
    db_order = Order(product_id=order.product_id, quantity=order.quantity, status="pending")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    logger.info(f"Order created: Product {order.product_id} x{order.quantity}")
    return {
        "message": "Order created successfully",
        "order_id": db_order.id,
        "status": "pending"
    }

# New endpoint to manually process an order
@router.post("/orders/{order_id}/process")
def process_specific_order(
    order_id: int = Path(..., title="The ID of the order to process"),
    db: Session = Depends(get_db)
):
    # Check if order exists
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
    
    # Send to Celery for processing
    order_data = {"product_id": order.product_id, "quantity": order.quantity}
    task = process_order.delay(order_data)
    
    logger.info(f"Manual processing triggered for Order {order_id}, Task ID: {task.id}")
    return {
        "message": f"Order {order_id} processing triggered",
        "order_id": order_id,
        "task_id": task.id
    }