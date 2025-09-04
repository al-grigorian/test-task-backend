from fastapi import FastAPI, Depends, HTTPException
import uvicorn
from contextlib import asynccontextmanager
from core.config import settings
from core.models import *
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy

class AddItemRequest(BaseModel):
    product_id: int
    quantity: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(lifespan=lifespan)


@app.post("/orders/{order_id}/add_item/")
async def add_item_to_order(
    order_id: int,
    item: AddItemRequest,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Количество должно быть больше 0")

    # Проверяем заказ
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    # Проверяем товар
    product = await session.get(Product, item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    if product.quantity <= item.quantity:
        raise HTTPException(status_code=400, detail="Недостаточно товара в наличии")

    # Проверяем наличие в заказе
    result = await session.execute(
        select(OrderItem).where(
            OrderItem.order_id == order_id, OrderItem.product_id == item.product_id
        )
    )
    order_item = result.scalar_one_or_none()

    if order_item:
        order_item.quantity += item.quantity
    else:
        order_item = OrderItem(
            order_id=order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price,
        )
        session.add(order_item)

    product.quantity -= item.quantity

    await session.commit()
    await session.refresh(order_item)

    return {
        "message": "Товар добавлен в заказ",
        "order_id": order_id,
        "product_id": item.product_id,
        "quantity": order_item.quantity,
    }

if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)