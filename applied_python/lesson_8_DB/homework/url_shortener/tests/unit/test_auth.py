import pytest
from auth import verify_password, get_password_hash, create_access_token, get_current_user
from fastapi import HTTPException
from jose import JWTError

def test_password_hashing():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_jwt_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

def test_get_current_user_invalid_token(mocker):
    mocker.patch("auth.jwt.decode", side_effect=JWTError())
    with pytest.raises(HTTPException):
        get_current_user(token="invalidtoken")