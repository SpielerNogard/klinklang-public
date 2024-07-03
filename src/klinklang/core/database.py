from peewee import DatabaseProxy, Model

db = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = db
