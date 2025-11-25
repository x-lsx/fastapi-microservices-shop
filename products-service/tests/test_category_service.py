import pytest
from unittest.mock import AsyncMock
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate

@pytest.mark.asyncio
async def test_create_category_success():
    mock_repo = AsyncMock()
    mock_repo.get_by_slug.return_value = None
    mock_repo.get_all.return_value = []
    mock_repo.create.return_value = {"id": 1, "name": "Test", "slug": "test"}

    service = CategoryService(db=None)
    service.repo = mock_repo

    data = CategoryCreate(name="Test", slug="test")
    cat = await service.create(data)

    assert cat["id"] == 1
    assert cat["name"] == "Test"
    assert cat['slug'] == "test"
    mock_repo.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_category_duplicate_slug():
    mock_repo = AsyncMock()
    mock_repo.get_by_slug.return_value = {"id": 1, "name": "Test", "slug": "test"}
    service = CategoryService(db=None)
    service.repo = mock_repo

    data = CategoryCreate(name="New", slug="test")
    with pytest.raises(ValueError) as e:
        await service.create(data)
    assert "already exists" in str(e.value)
