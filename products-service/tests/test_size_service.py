import pytest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from sqlalchemy.exc import IntegrityError

from app.services.size_service import SizeService
from app.schemas.size import SizeCreate, SizeUpdate


@pytest.mark.asyncio
async def test_list_and_get_calls_repo():
    """Проверяем получение списка размеров и конкретного размера по ID"""
    mock_repo = AsyncMock()
    mock_repo.get_all.return_value = [{"id": 1, "value": "S"}]
    mock_repo.get_by_id.return_value = {"id": 1, "value": "S"}

    svc = SizeService(db=None)
    svc.repo = mock_repo

    # Проверяем получение списка размеров
    res = await svc.list()
    assert isinstance(res, list)
    # Проверяем, что репозиторий вызывался ровно один раз
    mock_repo.get_all.assert_awaited_once()

    # Проверяем получение размера по ID
    got = await svc.get(1)
    assert got == {"id": 1, "value": "S"}
    # Проверяем, что репозиторий вызывался с правильным ID
    mock_repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_by_value():
    """Проверяем поиск размера по значению"""
    mock_repo = AsyncMock()
    mock_repo.get_by_value.return_value = {"id": 2, "value": "M"}
    svc = SizeService(db=None)
    svc.repo = mock_repo

    # Проверяем поиск по значению "M"
    res = await svc.get_by_value("M")
    assert res["value"] == "M"
    # Проверяем, что репозиторий вызывался с правильным значением
    mock_repo.get_by_value.assert_awaited_once_with("M")


@pytest.mark.asyncio
async def test_create_duplicate_and_success():
    """Проверяем создание размера: дубликат и успешное создание"""
    svc = SizeService(db=None)
    mock_repo = AsyncMock()
    svc.repo = mock_repo

    # ТЕСТ 1: Попытка создать дубликат
    # Настраиваем мок так, чтобы он нашел существующий размер
    mock_repo.get_by_value.return_value = SimpleNamespace(id=1, value="L")
    with pytest.raises(ValueError) as e:
        await svc.create(SizeCreate(value="L"))
    # Проверяем, что получили ошибку о существующем размере
    assert "already exists" in str(e.value)

    # ТЕСТ 2: Успешное создание размера
    # Настраиваем мок так, чтобы размер не нашелся (нет дубликата)
    mock_repo.get_by_value.return_value = None
    mock_repo.create.return_value = SimpleNamespace(id=3, value="XL")
    # Создаем новый размер
    res = await svc.create(SizeCreate(value="XL"))
    # Проверяем, что получили объект с правильным ID
    assert getattr(res, "id") == 3
    # Проверяем, что метод create репозитория был вызван
    mock_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_not_found_conflict_and_success():
    """Проверяем обновление размера: разные сценарии"""
    svc = SizeService(db=None)
    mock_repo = AsyncMock()
    svc.repo = mock_repo
    svc.db = AsyncMock()
    svc.db.rollback = AsyncMock()

    # ТЕСТ 1: Попытка обновить несуществующий размер
    mock_repo.get_by_id.return_value = None
    with pytest.raises(ValueError) as e:
        await svc.update(10, SizeUpdate(value="XXL"))
    # Проверяем, что получили ошибку "не найден"
    assert "not found" in str(e.value)

    # ТЕСТ 2: Конфликт - новое значение уже используется другим размером
    mock_repo.get_by_id.return_value = SimpleNamespace(id=5, value="S")
    mock_repo.get_by_value.return_value = SimpleNamespace(id=6, value="XXL")
    data = SizeUpdate(value="XXL")
    with pytest.raises(ValueError) as e2:
        await svc.update(5, data)
    # Проверяем, что получили ошибку о существующем значении
    assert "already exists" in str(e2.value)

    # ТЕСТ 3: Ошибка целостности базы данных при обновлении
    mock_repo.get_by_value.return_value = None
    def raise_integrity(*args, **kwargs):
        # Имитируем ошибку целостности БД
        raise IntegrityError("msg", params=None, orig=None)

    mock_repo.update.side_effect = raise_integrity
    with pytest.raises(ValueError) as e3:
        await svc.update(5, SizeUpdate(value="OK"))
    # Проверяем обработку ошибки целостности
    assert "Database integrity error" in str(e3.value)
    # Проверяем, что был выполнен rollback транзакции
    svc.db.rollback.assert_awaited()

    # ТЕСТ 4: Успешное обновление
    mock_repo.update.side_effect = None
    mock_repo.update.return_value = SimpleNamespace(id=5, value="OK")
    res = await svc.update(5, SizeUpdate(value="OK"))
    # Проверяем, что значение обновилось правильно
    assert getattr(res, "value") == "OK"


@pytest.mark.asyncio
async def test_delete_paths():
    """Проверяем удаление размера: неудача и успех"""
    svc = SizeService(db=None)
    mock_repo = AsyncMock()
    svc.repo = mock_repo

    # ТЕСТ 1: Неудачное удаление (размер не найден)
    mock_repo.delete.return_value = False
    with pytest.raises(ValueError):
        await svc.delete(1)

    # ТЕСТ 2: Успешное удаление
    mock_repo.delete.return_value = True
    # Проверяем, что исключение не выбрасывается
    await svc.delete(1)
    # Проверяем, что метод delete был вызван
    mock_repo.delete.assert_awaited()