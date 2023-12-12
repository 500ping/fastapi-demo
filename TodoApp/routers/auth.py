from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime

from TodoApp import models
from TodoApp.database import SessionLocal

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "7b267d32899e6d50a0a9565b08e578c19c450bee5f42e6b4ba1663b3b6517435"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class CreateUserResponse(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/auth", status_code=status.HTTP_201_CREATED, response_model=CreateUserResponse)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = models.Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return create_user_model


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(
        models.Users.username == username).first()
    if not user:
        return
    if not bcrypt_context.verify(password, user.hashed_password):
        return
    return user


def create_access_token(username: str, user_id, expires_delta: timedelta):
    encode = {
        "sub": username,
        "id": user_id,
        "exp": datetime.utcnow() + expires_delta,
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    username = form_data.username
    password = form_data.password

    if user := authenticate_user(username, password, db):
        return {
            "access_token": create_access_token(user.username, user.id, timedelta(minutes=20)),
            "token_type": "bearer"
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate ")


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate ")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate ")
