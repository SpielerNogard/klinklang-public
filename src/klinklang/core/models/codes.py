from klinklang.core.database import BaseModel
from peewee import CharField, TimestampField


class Codes(BaseModel):
    email = CharField(primary_key=True)
    inserted = TimestampField(utc=True)
    code = CharField()
