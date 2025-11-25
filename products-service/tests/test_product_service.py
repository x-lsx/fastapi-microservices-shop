import pytest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from fastapi import HTTPException

from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate


@pytest.mark.asyncio
async def test_list_calls_repo_get_all():
    # Мокаем репозиторий и его метод get_all
    mock_repo = AsyncMock()
    mock_repo.get_all.return_value = [
        {"id": 1, "name": "P1"},
        {"id": 2, "name": "P2"},
    ]

    # Создаем сервис и подменяем репозиторий моковым
    service = ProductService(db=None)
    service.product_repository = mock_repo

    # Вызываем метод list сервиса
    res = await service.list()

    # Проверяем, что результат список с нужным количеством элементов
    assert isinstance(res, list)
    assert len(res) == 2
    # Проверяем, что метод репозитория действительно вызвался
    mock_repo.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_found_and_not_found():
    service = ProductService(db=None)
    mock_repo = AsyncMock()
    service.product_repository = mock_repo

    # Сценарий: товар не найден -> ожидаем HTTPException 404
    mock_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as e:
        await service.get_by_id(1)
    assert e.value.status_code == 404

    # Сценарий: товар найден -> возвращаем объект
    product = {"id": 1, "name": "P1"}
    mock_repo.get_by_id.return_value = product
    res = await service.get_by_id(1)
    assert res == product


@pytest.mark.asyncio
async def test_get_by_category_slug():
    service = ProductService(db=None)
    mock_cat_repo = AsyncMock()
    mock_prod_repo = AsyncMock()

    service.category_repository = mock_cat_repo
    service.product_repository = mock_prod_repo

    # Сценарий: категория не найдена -> HTTPException 404
    mock_cat_repo.get_by_slug.return_value = None
    with pytest.raises(HTTPException) as e:
        await service.get_by_category_slug("missing")
    assert e.value.status_code == 404

    # Сценарий: категория найдена -> возвращаем список продуктов
    mock_cat_repo.get_by_slug.return_value = SimpleNamespace(slug="cat-slug")
    mock_prod_repo.get_by_category_slug.return_value = [{"id": 3, "name": "CProd"}]

    res = await service.get_by_category_slug("cat-slug")
    assert isinstance(res, list)
    # Проверяем, что метод репозитория вызвался с правильным slug
    mock_prod_repo.get_by_category_slug.assert_awaited_once_with("cat-slug")


@pytest.mark.asyncio
async def test_create_product_validations_and_success():
    db = AsyncMock()
    db.commit = AsyncMock()

    service = ProductService(db=db)
    mock_cat_repo = AsyncMock()
    mock_prod_repo = AsyncMock()

    service.category_repository = mock_cat_repo
    service.product_repository = mock_prod_repo

    # Сценарий: категория не существует -> HTTPException 400
    mock_cat_repo.get_by_id.return_value = None
    data = ProductCreate(name="P", description=None, price=1.0, category_id=5, sizes=[])
    with pytest.raises(HTTPException) as e:
        await service.create(data)
    assert e.value.status_code == 400

    # Сценарий: категория существует -> успешное создание продукта
    mock_cat_repo.get_by_id.return_value = SimpleNamespace(id=5)
    mock_prod_repo.create.return_value = SimpleNamespace(id=10)
    mock_prod_repo.get_by_id.return_value = {"id": 10, "name": "P"}

    res = await service.create(data)
    assert res == {"id": 10, "name": "P"}
    db.commit.assert_awaited_once()
    mock_prod_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_and_delete_paths():
    db = AsyncMock()
    db.commit = AsyncMock()

    service = ProductService(db=db)
    mock_cat_repo = AsyncMock()
    mock_prod_repo = AsyncMock()

    service.category_repository = mock_cat_repo
    service.product_repository = mock_prod_repo

    # --- UPDATE ---
    # Сценарий: обновление с несуществующей категорией -> HTTPException 400
    mock_cat_repo.get_by_id.return_value = None
    data = ProductUpdate(name="New", description="desc", price=10.0, category_id=99, sizes=[])
    with pytest.raises(HTTPException) as e:
        await service.update(1, data)
    assert e.value.status_code == 400

    # Сценарий: обновление несуществующего продукта -> HTTPException 404
    mock_cat_repo.get_by_id.return_value = SimpleNamespace(id=1)
    mock_prod_repo.update.return_value = None
    with pytest.raises(HTTPException) as e2:
        await service.update(1, ProductUpdate(name="n", description="d", price=1.0, category_id=1, sizes=[]))
    assert e2.value.status_code == 404

    # Сценарий: успешное обновление
    mock_prod_repo.update.return_value = True
    mock_prod_repo.get_by_id.return_value = {"id": 1, "name": "Updated"}
    res = await service.update(1, ProductUpdate(name="u", description="d", price=1.0, category_id=1, sizes=[]))
    assert res == {"id": 1, "name": "Updated"}
    db.commit.assert_awaited()

    # --- DELETE ---
    # Сценарий: продукт не найден -> HTTPException 404
    mock_prod_repo.delete.return_value = False
    with pytest.raises(HTTPException) as e3:
        await service.delete(5)
    assert e3.value.status_code == 404

    # Сценарий: успешное удаление
    mock_prod_repo.delete.return_value = True
    res = await service.delete(5)
    assert res == {"detail": "Product deleted"}
    db.commit.assert_awaited()
