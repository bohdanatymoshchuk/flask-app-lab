from datetime import datetime

from flask import current_app
from tinydb import TinyDB, Query

TABLE = 'products'


def get_db():
    return TinyDB(
        current_app.config['PRODUCTS_DB_PATH'],
        create_dirs=True, encoding='utf-8', indent=4, ensure_ascii=False,
    )


def init_storage():
    """Створює data/products.json, якщо файлу ще немає."""
    with get_db() as db:
        db.table(TABLE)


def get_all():
    with get_db() as db:
        return sorted(db.table(TABLE).all(), key=lambda p: p['id'])


def get_by_id(product_id):
    with get_db() as db:
        return db.table(TABLE).get(Query().id == product_id)


def create(data):
    with get_db() as db:
        table = db.table(TABLE)
        new_id = max((p['id'] for p in table.all()), default=0) + 1
        table.insert({
            'id': new_id,
            **data,
            'created_at': datetime.now().isoformat(timespec='seconds'),
        })
        return new_id


def update(product_id, data):
    data = {k: v for k, v in data.items() if k not in ('id', 'created_at')}
    with get_db() as db:
        return bool(db.table(TABLE).update(data, Query().id == product_id))


def delete(product_id):
    with get_db() as db:
        return bool(db.table(TABLE).remove(Query().id == product_id))