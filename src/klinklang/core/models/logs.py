from klinklang.core.database import BaseModel
from peewee import ForeignKeyField, UUIDField, TextField, TimestampField
from klinklang.core.models.worker import Worker


class Logs(BaseModel):
    id = UUIDField(primary_key=True)
    worker: ForeignKeyField(Worker, backref="logs")
    log = TextField()
    created_at = TimestampField(utc=True, resolution=10)
