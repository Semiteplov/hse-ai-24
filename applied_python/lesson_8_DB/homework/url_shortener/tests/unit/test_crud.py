import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from models import Link, Visit
from crud import (
    create_link,
    get_link_by_short_code,
    delete_link,
    update_link,
    get_link_stats,
    search_links_by_original_url,
    add_visit,
    cleanup_unused_links,
    get_expired_links,
    update_last_visited
)


def test_create_link_with_custom_alias(db_session: Session):
    link_data = {
        "original_url": "http://example.com",
        "short_code": "custom123",
        "user_id": 1
    }
    link = create_link(db_session, link_data)
    assert link.short_code == "custom123"
    assert db_session.query(Link).filter_by(short_code="custom123").first() is not None


def test_create_link_duplicate_alias(db_session: Session):
    link_data = {
        "original_url": "http://example.com",
        "short_code": "duplicate"
    }
    create_link(db_session, link_data)

    with pytest.raises(ValueError, match="Custom alias already taken"):
        create_link(db_session, link_data)


def test_delete_existing_link(db_session: Session):
    link = Link(short_code="todelete", original_url="http://example.com")
    db_session.add(link)
    db_session.commit()

    deleted = delete_link(db_session, "todelete")
    assert deleted is not None
    assert db_session.query(Link).filter_by(short_code="todelete").first() is None


def test_delete_non_existent_link(db_session: Session):
    assert delete_link(db_session, "nonexistent") is None


def test_update_link_url(db_session: Session):
    link = Link(short_code="toupdate", original_url="http://old.com")
    db_session.add(link)
    db_session.commit()

    updated = update_link(db_session, "toupdate", "http://new.com")
    assert updated.original_url == "http://new.com"
    assert db_session.query(Link).filter_by(short_code="toupdate").first().original_url == "http://new.com"


# Тесты для статистики и поиска
def test_get_link_stats_with_visits(db_session: Session):
    link = Link(short_code="withvisits", original_url="http://example.com")
    db_session.add(link)
    db_session.commit()

    add_visit(db_session, link)
    add_visit(db_session, link)

    stats = get_link_stats(db_session, "withvisits")
    assert len(stats.visits) == 2


def test_search_links_by_original_url(db_session: Session):
    links = [
        Link(short_code="test1", original_url="http://common.com"),
        Link(short_code="test2", original_url="http://common.com"),
        Link(short_code="test3", original_url="http://other.com")
    ]
    db_session.add_all(links)
    db_session.commit()

    results = search_links_by_original_url(db_session, "http://common.com")
    assert len(results) == 2
    assert {r.short_code for r in results} == {"test1", "test2"}


def test_cleanup_unused_links(db_session: Session):
    old_link = Link(
        short_code="old",
        original_url="http://old.com",
        created_at=datetime.now(timezone.utc) - timedelta(days=31),
        last_visited_at=datetime.now(timezone.utc) - timedelta(days=31)
    )
    new_link = Link(
        short_code="new",
        original_url="http://new.com",
        created_at=datetime.now(timezone.utc) - timedelta(days=10)
    )
    db_session.add_all([old_link, new_link])
    db_session.commit()

    with patch('crud.delete_cached_url') as mock_del_cache, \
            patch('crud.remove_from_popular') as mock_del_popular:
        removed = cleanup_unused_links(db_session, max_days=30)

        assert len(removed) == 1
        assert removed[0].short_code == "old"
        mock_del_cache.assert_called_once_with("old")
        mock_del_popular.assert_called_once_with("old")
        assert db_session.query(Link).count() == 1


def test_get_expired_links(db_session: Session):
    expired = Link(
        short_code="expired",
        original_url="http://expired.com",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1)
    )
    active = Link(
        short_code="active",
        original_url="http://active.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1)
    )
    db_session.add_all([expired, active])
    db_session.commit()

    results = get_expired_links(db_session)
    assert len(results) == 1
    assert results[0].short_code == "expired"
