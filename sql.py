# -*- coding: utf-8 -*-
import peewee

# データベースを指定
db = peewee.SqliteDatabase("data.db")


# Define models
class User(peewee.Model):
    userId = peewee.PrimaryKeyField()
    name = peewee.TextField()
    email = peewee.TextField()

    class Meta:
        database = db


class Crop(peewee.Model):
    cropId = peewee.PrimaryKeyField()
    name = peewee.TextField()
    supplier = peewee.ForeignKeyField(User)
    expected_day = peewee.DateField(null=True)
    on_process = peewee.BooleanField(default=True)
    on_sale = peewee.BooleanField(default=False)
    sold_out = peewee.BooleanField(default=False)
    latitude = peewee.FloatField(default=200)
    longitude = peewee.FloatField(default=200)
    img_url = peewee.TextField(default="")

    class Meta:
        database = db


if __name__ == '__main__':
    User.create_table()
    Crop.create_table()
