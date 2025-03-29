from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import main
import pytest
from fastapi.testclient import TestClient
from main import generate_short_code, lifespan, app
from models import User, Link


@pytest.fixture
def client():
    return TestClient(app)


def test_generate_short_code():
    code = generate_short_code()
    assert len(code) == 6
    assert all(c.isalnum() for c in code)

    custom_length = generate_short_code(8)
    assert len(custom_length) == 8


@pytest.mark.asyncio
@patch('main.Base.metadata.create_all')
async def test_lifespan(mock_create):
    mock_app = MagicMock()
    async with lifespan(mock_app) as _:
        mock_create.assert_called_once_with(bind=main.engine)


# Тесты для роутов
@patch('main.create_link')
@patch('main.set_cached_url')
def test_shorten_link(mock_cache, mock_create, client, auth_headers):
    mock_create.return_value = Link(
        id=1,
        short_code='abc123',
        original_url='http://test.com',
        user_id=1,
        created_at=datetime.now(timezone.utc),
        expires_at=None
    )

    response = client.post("/links/shorten", json={"original_url": "http://test.com"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['short_code'] == 'abc123'

    mock_create.return_value = Link(
        id=2,
        short_code='test',
        original_url='http://test.com',
        user_id=1,
        created_at=datetime.now(timezone.utc),
        expires_at=None
    )

    response = client.post("/links/shorten", json={
        "original_url": "http://test.com",
        "custom_alias": "custom"
    }, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()['short_code'] == 'test'


@patch('main.get_expired_links')
def test_get_expired_links(mock_expired, client):
    mock_expired.return_value = []
    response = client.get("/links/expired")
    assert response.status_code == 200


@patch('main.search_links_by_original_url')
def test_search_links(mock_search, client):
    mock_search.return_value = []
    response = client.get("/links/search?original_url=http://test.com")
    assert response.status_code == 200


@patch('main.get_link_stats')
def test_get_link_stats_not_found(mock_get_stats, client):
    mock_get_stats.return_value = None
    response = client.get("/links/notfound/stats")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch('main.get_link_by_short_code')
def test_update_link_forbidden(mock_get, client, auth_headers):
    mock_get.return_value = Link(
        id=1,
        short_code='abc123',
        original_url='http://old.com',
        user_id=1,
        created_at=datetime.now(timezone.utc)
    )

    with patch('main.get_current_user', return_value=User(id=2)):
        response = client.put(
            "/links/abc123",
            json={"new_url": "http://new.com"},
            headers=auth_headers
        )

        assert response.status_code == 403
        assert "Not your link" in response.json()['detail']


@patch('main.cleanup_unused_links')
def test_cleanup_links_invalid_days(mock_cleanup, client):
    response = client.delete("/cleanup-unused-links?n_days=0")
    assert response.status_code == 422


# Тесты для аутентификации
@patch('main.get_password_hash')
def test_register_existing_user(mock_hash, client):
    mock_hash.return_value = 'hashed'
    client.post("/register", json={"username": "test", "password": "pass"})
    response = client.post("/register", json={"username": "test", "password": "pass"})
    assert response.status_code == 400
    assert "already taken" in response.json()['detail']


@patch('main.verify_password')
def test_login_invalid_credentials(mock_verify, client):
    mock_verify.return_value = False
    response = client.post("/login",
                           data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 400
