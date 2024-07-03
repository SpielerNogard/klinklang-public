from klinklang.core.database import BaseModel
from peewee import CharField, TimestampField, BooleanField, IntegerField


class Proxy(BaseModel):
    ip= CharField(primary_key=True)
    rotating= BooleanField(default=False)
    region= CharField()
    consecutive_failures: IntegerField(default=0)
    last_used = TimestampField(utc=True)
    next_use = TimestampField(utc=True)
