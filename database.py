import datetime
import os

from peewee import *

db_dir = os.path.join(os.path.dirname(__file__), 'photo.db')
db = SqliteDatabase(db_dir)


class BaseModel(Model):
    class Meta:
        database = db


class Photo(BaseModel):
    # ID = IntegerField(unique=True)
    unique_id = IntegerField(unique=True)
    photo_id = IntegerField()
    owner_id = IntegerField()
    message_id = IntegerField()
    access_key = CharField()
    photo_url = CharField()
    text = CharField()
    date = DateTimeField(default=datetime.datetime.now().replace(microsecond=0))

    @classmethod
    def get_photo(cls, unique_id):
        try:
            obj = cls.get(unique_id=unique_id)
            return obj
        except DoesNotExist:
            return False

    @classmethod
    def update_text(cls,obj, text):
        obj.text = text
        obj.save()

    @classmethod
    async def change_value(cls, user_id, title, value):
        user = cls.get_user(user_id)
        setattr(user, title, value)
        user.save()

    @classmethod
    def create_photo(cls, photo_id, owner_id, access_key, photo_url, text):
        cls.create(photo_id=photo_id, owner_id=owner_id, access_key=access_key, photo_url=photo_url, text=text)

    @classmethod
    def photo_exists(cls, unique_id):
        query = cls().select().where(cls.unique_id == unique_id)
        print(query)
        return query.exists()

    @classmethod
    def get_all_photo(cls, owner_id):
        query = cls().select().where(cls.owner_id == owner_id)
        return query


def add_photo():
    owner_id  = photo_id = text = access_key = photo_url = 1
    message_id = 3
    Photo.create(unique_id=int(f'{owner_id}{message_id}'),
                 photo_id=photo_id,
                 owner_id=owner_id,
                 message_id=message_id,
                 access_key=access_key,
                 photo_url=photo_url,
                 text=text)


if __name__ == '__main__':
    # Photo.create()
    db.create_tables([Photo])
    # add_photo()
    # obj = Photo.get(unique_id=13)
    # obj.delete_instance()
    # obj = Photo.get_all_photo(owner_id=1)
    # obj[0].delete_instance()
    # print(obj[0].owner_id)
    # print(list(obj.owner))

    # unique_id = 11
    # obj = Photo.get_photo(unique_id=unique_id)
    # obj.text = 'asfs'
    # obj.save()
    pass
