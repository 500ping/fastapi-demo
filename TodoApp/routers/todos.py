from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Path
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from TodoApp import models
from TodoApp.database import SessionLocal
from .auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    phone_number: str


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todos = db.query(models.Todos).filter(
        models.Todos.owner_id == user.get("id")).all()
    return todos


@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(
        models.Todos.owner_id == user.get("id")).first()
    if todo:
        return todo
    raise HTTPException(status_code=404, detail="Todo not found!")


@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = models.Todos(
        **todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.put("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(
        models.Todos.id == todo_id).first()

    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found!")

    todo_dict = jsonable_encoder(todo_model)
    request_dict = todo_request.model_dump()
    for field, value in todo_dict.items():
        if field in request_dict and value != request_dict[field]:
            setattr(todo_model, field, request_dict[field])
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(
        models.Todos.id == todo_id).first()

    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found!")

    db.delete(todo_model)
    db.commit()
