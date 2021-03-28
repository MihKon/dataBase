from sqlalchemy.orm import Session
from . import models, schemas
# from typing import Optional


def delete_item_by_id(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).one()
    db.delete(db_item)
    db.commit()
    # db.refresh(db_item)
    return db_item


def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def get_item_by_id(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).one()


def get_item_by_field(db: Session, field: str):
    return db.query(models.Item).filter(models.Item.field1 == field or models.Item.field2 == field).one()


def update_item_by_id(db: Session, item: schemas.ItemCreate):
    db.query(models.Item).filter(models.Item.id == item.id).\
        update({"field1": item.field1, "field2": item.field2})
    db.commit()
    return db.query(models.Item).filter(models.Item.id == item.id).one()
