import datetime
from flask_peewee.admin import Admin, ModelAdmin
from psyc.auth import auth
from psyc.database import db
from peewee import *

class Execution(db.Model):
    user         = ForeignKeyField(auth.User)
    execution_id = CharField()
    sent  = DateTimeField(default=datetime.datetime.now)
    parameters = CharField(null=True)
    access_token =  CharField(null=True)
    result   =  TextField(null=True)
    received = DateTimeField(default=0)

class ExecutionAdmin(ModelAdmin):
    columns = ('user', 'execution_id', 'sent', 'parameters', 'received')

def add(user,execution_id, access_token, parameters):
    ex = Execution(user=user,execution_id=execution_id, access_token=access_token, parameters=parameters)
    ex.save()

def update(execution_id, result):
    try:
       execution = Execution.get(Execution.execution_id == execution_id)
       execution.result = result
       execution.received = datetime.datetime.now() 
       execution.save()
       return execution
    except Execution.DoesNotExist:
       return None 

def fetch_by_id(execution_id):
    try:
       execution = Execution.get(Execution.execution_id == execution_id)
       return execution
    except Execution.DoesNotExist:
       return None 

def fetch_results_for_user(user):
   
    try:
        executions = Execution.select().where(Execution.user==user).order_by(Execution.received.desc())
        return dict(((e.execution_id, e.result) for e in executions))
    except: 
        pass
        
    return {}
    
def fetch_latest_results_by_user(user):
    try:
        executions = Execution.select().where(Execution.user==user).order_by(Execution.received.desc()).limit(1)
        for execution in executions:
            return execution.result
    except: 
        return None  

    return None
