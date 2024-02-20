from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src import schemas
from src.database import get_db
from src.internal.crud import item as crud
from src.internal.crud import user as usercrud

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[schemas.Item])
def get_items(db: Session = Depends(get_db)):
    """
    Возвращает список элементов.
    """
    return crud.get_items(db=db)


@router.get("/{id}", response_model=schemas.Item)
def get_item_by_id(id: int, db: Session = Depends(get_db)):
    """
    Возвращает элемент по указанному ID.
    """
    db_item = crud.get_item_by_id(id=id, db=db)
    # Если такого элемента нет, то возвращаем ошибку 404
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_item


@router.post(
    "/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED
)
def create_item(new_item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """
    Создает новый элемент.
    """
    # Ищем user c id равным user_id
    db_user = usercrud.get_user_by_id(id=new_item.user_id, db=db)
    # Если такого user нет то возвращаем ошибку 404
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return crud.create_item(item=new_item, db=db)


@router.put("/{id}", response_model=schemas.Item)
def update_item(
    id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    """
    Обновляет поля элемента по указанному ID.
    """
    # Проверяем есть ли такой ID в items
    db_item = crud.get_item_by_id(id=id, db=db)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    # Проверяем есть ли user c id == user_id
    if db_item.user_id != item.user_id:
        check = usercrud.get_user_by_id(id=item.user_id, db=db)
        if check is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
    return crud.update_item(db_item=db_item, item=item, db=db)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
def delete_item(id: int, db: Session = Depends(get_db)):
    """
    Удаляет элемент по указанному ID.
    """
    # Проверяем есть ли такой ID в items
    db_item = crud.get_item_by_id(id=id, db=db)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    # Удаляем
    crud.delete_item(db_item=db_item, db=db)
    # Возвращаем ответ без контента
    return Response(status_code=status.HTTP_204_NO_CONTENT)
