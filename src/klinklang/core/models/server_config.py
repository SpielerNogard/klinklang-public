from klinklang.core.database import BaseModel
from peewee import CharField, TextField, TimestampField


class ServerConfig(BaseModel):
    name = CharField(primary_key=True)
    value = TextField()
    last_updated = TimestampField(utc=True)
