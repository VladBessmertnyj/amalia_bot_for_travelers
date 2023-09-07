import peewee as pw


db = pw.SqliteDatabase('queries.db')


class ModelBase(pw.Model):

    class Meta:
        database = db


class History(ModelBase):
    created_at = pw.DateTimeField()
    user_id = pw.IntegerField()
    command = pw.TextField()
    hotels = pw.TextField()
