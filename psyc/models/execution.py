import datetime
from flask_peewee.admin import Admin, ModelAdmin
from psyc.auth import auth
from psyc.database import db
from peewee import *

class ExecutionRequest(db.Model):
    execution_id = CharField() 
    parameters = CharField()
    sent  = DateTimeField(default=datetime.datetime.now) 

class ExecutionRequestAdmin(ModelAdmin):
    columns = ('execution_id', 'parameters', 'sent')   

class ExecutionResponse(db.Model):
    execution_id =  CharField()
    access_token =  CharField() 
    result   =  TextField()
    received = DateTimeField(default=datetime.datetime.now) 

class ExecutionResponseAdmin(ModelAdmin):
    columns = ('execution_id', 'access_token', 'result', 'received')
