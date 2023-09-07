from typing import List, Dict, TypeVar

from peewee import ModelSelect

from database.common.models import db, History

T = TypeVar('T')


def _store_data(database: db, model: T, *data: List[Dict]) -> None:
    with database.atomic():
        model.insert_many(*data).execute()


def _retrieve_all_data(database: db, model: T, user_id: int) -> ModelSelect:
    with database.atomic():
        response = model.select().where(model.user_id == user_id).order_by(model.created_at.desc())

    return response


class CRUDInterface:

    @classmethod
    def add_data(cls, data):
        return _store_data(db, History, data)

    @classmethod
    def retrieve_data(cls, user_id):
        return _retrieve_all_data(db, History, user_id)


crud = CRUDInterface
