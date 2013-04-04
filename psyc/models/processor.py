import catalog
import resource
from flask_peewee.admin import Admin, ModelAdmin
from flask_peewee.rest import RestResource
from flask_peewee.rest import RestrictOwnerResource
from psyc.auth import auth
from psyc.database import db
from peewee import *
import json

class Processor(db.Model):
   catalog = ForeignKeyField(catalog.Catalog)
   resource = ForeignKeyField(resource.Resource)
   state = TextField()
   expiry  = IntegerField()
   query   = CharField()
   code     = CharField(null=True)
   token    = CharField(null=True)
   status   = CharField(default="pending")
          
class ProcessorAdmin(ModelAdmin):
   columns = ('catalog', 'resource', 'expiry', 'query', 'token', 'status')

class ProcessorResource(RestrictOwnerResource):
    exclude = ('state', 'code', 'token')
    owner_field = 'user'
    
def fetch_by_resource(resource):
    
    try:
        processor = Processor.select().where(Processor.resource == resource) 
        if processor.count() > 0:
            return processor 
            
    except Processor.DoesNotExist:
        return None  

    return None

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
