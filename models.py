from peewee import *

db = SqliteDatabase("app.db")


class Participant(Model):
    username = CharField(max_length=30)
    name = CharField(max_length=255)
    company_name = TextField()
    domain = TextField()
    position = TextField()
    phone_num = TextField()

    class Meta:
        database = db

Participant.create_table()
