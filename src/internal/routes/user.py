from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src import schemas
from src.database import get_db
from src.internal.crud import user as crud

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[schemas.User])
def get_users(db: Session = Depends(get_db)):
    """
    Возвращает список пользователей.
    """
    return crud.get_users(db=db)


@router.get("/{id}", response_model=schemas.User)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    """
    Возвращает пользователя по указанному ID.
    """
    # Ищем пользователя с таким ID
    db_user = crud.get_user_by_id(id=id, db=db)
    # Если такого пользователя нет, то возвращаем ошибку 404
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@router.post(
    "/", response_model=schemas.User, status_code=status.HTTP_201_CREATED
)
def create_user(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Создает нового пользователя.
    """
    # Ищем пользователя с новым email
    db_user = crud.get_user_by_email(email=new_user.email, db=db)
    # Если пользователь найден, то возвращаем ошибку 400
    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use",
        )
    return crud.create_user(user=new_user, db=db)


@router.put("/{id}", response_model=schemas.User)
def update_user(
    id: int, user: schemas.UserCreate, db: Session = Depends(get_db)
):
    """
    Обновляет поля пользователя по указанному ID.
    """
    # Ищем пользователя по указанному id
    db_user = crud.get_user_by_id(id=id, db=db)
    # Если пользователь найден, то возвращаем ошибку 404
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # Если изменилось поле email
    if db_user.email != user.email:
        # Проверяем не занят ли новый email
        check = crud.get_user_by_email(email=user.email, db=db)
        # Если занят, возвращаем ошибку 400
        if check is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
    return crud.update_user(db_user=db_user, user=user, db=db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    """
    Удаляет пользователя по указанному ID.
    """
    # Ищем пользователя по указанному id
    db_user = crud.get_user_by_id(id=id, db=db)
    # Если пользователь найден, то возвращаем ошибку 404
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # Удаляем
    crud.delete_user(db_user=db_user, db=db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
