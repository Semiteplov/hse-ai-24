from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from cache import delete_cached_url, remove_from_popular
from models import Link, Visit


def create_link(db: Session, link_data):
    if link_data.get("short_code"):
        existing = db.query(Link).filter(Link.short_code == link_data["short_code"]).first()
        if existing:
            raise ValueError("Custom alias already taken")
    db_link = Link(**link_data)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


def get_link_by_short_code(db: Session, short_code: str):
    return db.query(Link).filter(Link.short_code == short_code).first()


def delete_link(db: Session, short_code: str):
    db_link = get_link_by_short_code(db, short_code)
    if db_link:
        db.delete(db_link)
        db.commit()
    return db_link


def update_link(db: Session, short_code: str, new_url: str):
    db_link = get_link_by_short_code(db, short_code)
    if db_link:
        db_link.original_url = new_url
        db.commit()
        db.refresh(db_link)
    return db_link


def get_link_stats(db: Session, short_code: str):
    db_link = get_link_by_short_code(db, short_code)
    if db_link:
        return db_link
    return None


def search_links_by_original_url(db: Session, original_url: str):
    return db.query(Link).filter(Link.original_url == original_url).all()


def add_visit(db: Session, link: Link):
    visit = Visit(link_id=link.id)
    db.add(visit)
    update_last_visited(db, link)
    db.commit()
    db.refresh(visit)


def cleanup_unused_links(db: Session, max_days: int):
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    unused_links = db.query(Link).filter(
        (Link.last_visited_at < cutoff) | ((Link.last_visited_at.is_(None)) & (Link.created_at < cutoff))
    ).all()
    for link in unused_links:
        db.delete(link)
        delete_cached_url(link.short_code)
        remove_from_popular(link.short_code)
    db.commit()
    return unused_links


def get_expired_links(db: Session):
    now = datetime.now(timezone.utc)
    return db.query(Link).filter(Link.expires_at != None).filter(Link.expires_at < now).all()


def update_last_visited(db: Session, link: Link):
    link.last_visited_at = datetime.now(timezone.utc)
    db.commit()
