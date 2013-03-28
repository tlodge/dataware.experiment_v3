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
   code     = CharField(null=True)
   token    = CharField(null=True)
   status   = CharField(default="pending")

class ProcessorAdmin(ModelAdmin):
   columns = ('catalog', 'resource', 'expiry', 'query', 'token', 'status')

def updateProcessorRequest(state, status, code=None, token=None):
    processor = None

    try:
       processor = Processor.get(Processor.state == state)
    except Processor.DoesNotExist:
       return processor 

    if code is not None:
       processor.code = code
    
    if token is not None:
       processor.token = token

    processor.status = status
    
    processor.save()
    return processor
