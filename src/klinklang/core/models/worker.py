import datetime

from pydantic import BaseModel

from sqlmodel import Field, SQLModel

class Worker(SQLModel, table=True):
    id: str = Field(primary_key=True)
    last_seen: datetime.datetime = Field(default=datetime.datetime.fromtimestamp(1, tz=datetime.timezone.utc))

from peewee import MySQLDatabase, Model, CharField, ForeignKeyField, TextField, DateTimeField, BooleanField, TimestampField
import datetime


db = MySQLDatabase(database='mydatabase', host='localhost', user='root', password='password')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)

class Tweet(BaseModel):
    user = ForeignKeyField(User, backref='tweets')
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    is_published = BooleanField(default=True)
    test=TextField()

class ServerConfig(BaseModel):
    name =CharField(unique=True)
    value =TextField()
    last_updated = TimestampField(utc=True)

if __name__ == "__main__":
    db.connect()
    db.drop_tables([User, Tweet, ServerConfig])
    db.create_tables([User, Tweet, ServerConfig])

