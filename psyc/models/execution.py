import datetime
from flask_peewee.admin import Admin, ModelAdmin
from psyc.auth import auth
from psyc.database import db
from peewee import *

class Execution(db.Model):
    execution_id = CharField()
    sent  = DateTimeField(default=datetime.datetime.now)
    parameters = CharField(null=True)
    access_token =  CharField(null=True)
    result   =  TextField(null=True)
    received = DateTimeField(default=0)

class ExecutionAdmin(ModelAdmin):
    columns = ('execution_id', 'sent', 'parameters', 'received')

def add(execution_id, access_token, parameters):
    ex = Execution(execution_id=execution_id, access_token=access_token, parameters=parameters)
    ex.save()

def update(execution_id, result):
    try:
       execution = Execution.get(Execution.execution_id == execution_id)
       execution.result = result
       execution.received = datetime.datetime.now() 
       execution.save()
    except Execution.DoesNotExist:
       return None 
