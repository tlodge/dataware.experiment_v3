import datetime
import catalog
from flask_peewee.admin import Admin, ModelAdmin
from psyc.auth import auth 
from psyc.database import db
from peewee import *

class Url(db.Model):
  user = ForeignKeyField(auth.User, related_name='urls')
  ts = IntegerField()
  macaddr = TextField()
  ipaddr = TextField()
  url = TextField()

class UrlAdmin(ModelAdmin):
  columns = ('user', 'macaddr', 'ipaddr', 'url')

class Resource(db.Model):
  user = ForeignKeyField(auth.User, related_name='resources')
  catalog_uri = TextField() 
  owner = TextField()
  resource_name = TextField()

class ResourceAdmin(ModelAdmin):
  columns = ('user', 'catalog_uri', 'owner', 'resource_name')
