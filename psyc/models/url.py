from flask_peewee.admin import Admin, ModelAdmin
from psyc.auth import auth 
from psyc.database import db
from peewee import *

class Url(db.Model):
  user = ForeignKeyField(auth.User, related_name='urls')
  ts = IntegerField()
  macaddr = CharField()
  ipaddr = CharField()
  url = CharField()

class UrlAdmin(ModelAdmin):
  columns = ('user', 'macaddr', 'ipaddr', 'url')

