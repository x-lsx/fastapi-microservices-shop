import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.cart import CartService

# Вспомогательная функция для создания "корзины" в виде объекта SimpleNamespace
def make_cart(items=None):
    if items is None:
        items = []
    cart = SimpleNamespace()
    cart.items = items
    return cart

# Вспомогательная функция для создания "элемента корзины"
def make_item(product_id, size_id, quantity, price=1.0):
    return SimpleNamespace(product_id=product_id, size_id=size_id, quantity=quantity, price=price)


# -------------------
# Тест: получение корзины
# Если корзина отсутствует, должна создаться новая
# -------------------
@pytest.mark.asyncio
async def test_get_cart_creates_if_missing():
    repo = AsyncMock()
    repo.get_cart.return_value = None  # корзина отсутствует
    repo.create_cart.return_value = make_cart()  # возвращаем новую корзину

    client = AsyncMock()
    svc = CartService(db=None, product_client=client)
    svc.repo = repo

    cart = await svc.get_cart(1)
    assert cart is not None
    repo.create_cart.assert_awaited_once_with(1)  # проверяем, что метод создания корзины вызвался


# -------------------
# Тест: добавление элемента в корзину
# Проверяем два кейса:
# 1) Элемент уже есть → увеличиваем количество
# 2) Новый элемент → добавляем через add_item
# -------------------
@pytest.mark.asyncio
async def test_add_item_existing_and_new():
    # существующий элемент
    item = make_item(10, 1, 2, price=5.0)
    cart = make_cart([item])

    repo = AsyncMock()
    repo.get_cart.return_value = cart
    repo.create_cart.return_value = cart

    client = AsyncMock()
    client.validate_product_and_size.return_value = {"product": {"price": 5.0}}

    svc = CartService(db=None, product_client=client)
    svc.repo = repo

    # добавляем количество к существующему элементу
    res = await svc.add_item(1, 10, 1, 3)
    assert item.quantity == 5  # 2 + 3 = 5
    repo.update_item.assert_awaited()

    # добавляем новый элемент
    cart2 = make_cart([])
    repo.get_cart.return_value = cart2
    await svc.add_item(1, 20, 2, 1)
    repo.add_item.assert_awaited()


# -------------------
# Тест: удаление элемента из корзины
# Проверяем ветки:
# - элемент отсутствует → должно поднять HTTPException
# - элемент существует → удаляем через remove_item
# -------------------
@pytest.mark.asyncio
async def test_remove_item_paths():
    repo = AsyncMock()
    cart = make_cart([])
    repo.get_cart.return_value = cart

    client = AsyncMock()
    svc = CartService(db=None, product_client=client)
    svc.repo = repo

    # удаляем несуществующий элемент → исключение
    with pytest.raises(HTTPException):
        await svc.remove_item(1, 1, 1)

    # удаляем существующий элемент
    item = make_item(1, 1, 2)
    cart.items = [item]
    repo.get_cart.return_value = cart
    await svc.remove_item(1, 1, 1)
    repo.remove_item.assert_awaited_with(item)


# -------------------
# Тест: изменение количества элемента
# Проверяем разные ветки:
# - delta=0 → просто возвращаем корзину
# - элемент отсутствует и delta>0 → добавляем
# - элемент отсутствует и delta<0 → исключение
# - элемент существует и новая quantity <=0 → удаляем
# - элемент существует и delta>0 → обновляем
# -------------------
@pytest.mark.asyncio
async def test_change_item_quantity_branches():
    repo = AsyncMock()
    client = AsyncMock()
    svc = CartService(db=None, product_client=client)
    svc.repo = repo

    # delta == 0 → возвращаем корзину без изменений
    cart = make_cart([])
    repo.get_cart.return_value = cart
    res = await svc.change_item_quantity(1, 1, 1, 0)
    assert res is cart

    # элемент не найден & delta>0 → вызываем add_item
    repo.get_cart.return_value = cart
    client.validate_product_and_size.return_value = {"product": {"price": 2.0}}
    await svc.change_item_quantity(1, 2, 1, 3)
    repo.add_item.assert_awaited()

    # элемент не найден & delta<0 → исключение
    with pytest.raises(HTTPException):
        await svc.change_item_quantity(1, 99, 1, -1)

    # элемент существует & новая quantity <=0 → удаляем
    item = make_item(5, 1, 1)
    cart.items = [item]
    repo.get_cart.return_value = cart
    await svc.change_item_quantity(1, 5, 1, -1)
    repo.remove_item.assert_awaited_with(item)

    # элемент существует & delta>0 → обновляем количество
    item = make_item(6, 2, 1)
    cart.items = [item]
    repo.get_cart.return_value = cart
    client.validate_product_and_size.return_value = {"product": {"price": 3.0}}
    await svc.change_item_quantity(1, 6, 2, 2)
    repo.update_item.assert_awaited()


# -------------------
# Тест: очистка корзины
# Проверяем, что remove_item вызывается для всех элементов
# -------------------
@pytest.mark.asyncio
async def test_clear_cart_removes_all_items():
    repo = AsyncMock()
    item1 = make_item(1, 1, 1)
    item2 = make_item(2, 1, 2)
    cart = make_cart([item1, item2])
    repo.get_cart.return_value = cart

    client = AsyncMock()
    svc = CartService(db=None, product_client=client)
    svc.repo = repo

    res = await svc.clear_cart(1)
    # remove_item вызван дважды, по одному на каждый элемент
    assert repo.remove_item.await_count == 2
    assert res is cart
