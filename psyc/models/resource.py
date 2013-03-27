from flask_peewee.admin import Admin, ModelAdmin
from psyc.auth import auth
from psyc.database import db
from peewee import *

class Resource(db.Model):
  user = ForeignKeyField(auth.User, related_name='resources')
  catalog_uri = CharField()
  owner = CharField()
  resource_name = CharField()

class ResourceAdmin(ModelAdmin):
  columns = ('user', 'catalog_uri', 'owner', 'resource_name')
