import catalog
import resource
from flask_peewee.admin import Admin, ModelAdmin
from psyc.auth import auth
from psyc.database import db
from peewee import *

class Processor(db.Model):
   state = TextField()
   catalog = ForeignKeyField(catalog.Catalog)
   resource = ForeignKeyField(resource.Resource)
   expiry  = IntegerField()
   query   = CharField()
   redirect = CharField()
   code     = CharField(null=True)
   token    = CharField(null=True)
   status   = CharField(null=True)

class ProcessorAdmin(ModelAdmin):
   columns = ('catalog', 'resource', 'expiry', 'query', 'status')
