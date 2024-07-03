from peewee import (
    BooleanField,
    CharField,
    TimestampField,
)

from klinklang.core.database import BaseModel


class Worker(BaseModel):
    id = CharField(primary_key=True)
    last_seen = TimestampField(utc=True)
    is_active = BooleanField(default=True)
