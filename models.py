import datetime
from peewee import *


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase("search_terms.db")


class SearchTerm(BaseModel):
    phrase = CharField()

    def __unicode__(self):
        return self.phrase

    def parse(self):
        # TODO: we will add this method in a bit.
        pass

    def test(self, title):
        # TODO: we will add this method in a bit.
        pass


class SavedLink(BaseModel):
    title = CharField(max_length=255)
    url = CharField(index=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
