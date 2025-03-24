import logging
import random
import string
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Sequence

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import get_password_hash, verify_password, create_access_token, get_current_user
from cache import get_cached_url, set_cached_url, delete_cached_url, increment_link_score, remove_from_popular
from crud import create_link, get_link_by_short_code, delete_link, get_link_stats, search_links_by_original_url, \
    add_visit, cleanup_unused_links, get_expired_links
from db import SessionLocal, Base, engine
from models import User
from schemas import LinkCreate, LinkResponse, LinkStatsResponse, LinkUpdate, UserCreate, Token


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
logging.basicConfig(level=logging.INFO)


def generate_short_code(length: int = 6) -> str:
    chars: Sequence[str] = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/links/shorten", response_model=LinkResponse)
def shorten_link(link: LinkCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    short_code = link.custom_alias if link.custom_alias else generate_short_code()
    db_link = create_link(db, {
        "original_url": link.original_url,
        "short_code": short_code,
        "expires_at": link.expires_at,
        "user_id": user.id
    })
    set_cached_url(short_code, link.original_url)
    return db_link


@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    cached_url = get_cached_url(short_code)
    if cached_url:
        return RedirectResponse(url=cached_url.decode("utf-8"))
    db_link = get_link_by_short_code(db, short_code)
    if db_link:
        set_cached_url(short_code, db_link.original_url)
        return RedirectResponse(url=db_link.original_url)
    raise HTTPException(status_code=404, detail="Link not found")


@app.get("/links/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    cached_url = get_cached_url(short_code)
    db_link = get_link_by_short_code(db, short_code)
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")

    expires_at = db_link.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at and expires_at < datetime.now(timezone.utc):
        delete_link(db, short_code)
        delete_cached_url(short_code)
        raise HTTPException(status_code=410, detail="Link has expired")

    add_visit(db, db_link)
    increment_link_score(short_code)

    if cached_url:
        return RedirectResponse(url=cached_url.decode("utf-8"))

    set_cached_url(short_code, db_link.original_url)
    return RedirectResponse(url=db_link.original_url)


@app.get("/links/{short_code}/stats", response_model=LinkStatsResponse)
def get_link_statistics(short_code: str, db: Session = Depends(get_db)):
    db_link = get_link_stats(db, short_code)
    if db_link:
        return db_link
    raise HTTPException(status_code=404, detail="Link not found")


@app.put("/links/{short_code}", response_model=LinkResponse)
def update_short_link(short_code: str, data: LinkUpdate, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    db_link = get_link_by_short_code(db, short_code)
    if not db_link or db_link.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your link")
    db_link.original_url = data.new_url
    db.commit()
    db.refresh(db_link)
    return db_link


@app.get("/links/search", response_model=list[LinkResponse])
def search_links(original_url: str, db: Session = Depends(get_db)):
    links = search_links_by_original_url(db, original_url)
    return links


@app.delete("/cleanup-unused-links", response_model=list[LinkResponse])
def cleanup_links(n_days: int = Query(30, ge=1), db: Session = Depends(get_db)):
    """Удаляет ссылки, не использованные более N дней"""
    removed = cleanup_unused_links(db, max_days=n_days)
    return removed


@app.get("/links/expired", response_model=list[LinkResponse])
def get_expired(db: Session = Depends(get_db)):
    """Список истекших ссылок"""
    return get_expired_links(db)


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = get_password_hash(user.password)
    db_user = User(username=user.username)
    db_user.password_hash = hashed
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created"}


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.delete("/links/{short_code}")
def delete_short_link(short_code: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_link = get_link_by_short_code(db, short_code)
    if not db_link or db_link.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your link")
    delete_cached_url(short_code)
    remove_from_popular(short_code)
    return delete_link(db, short_code)
