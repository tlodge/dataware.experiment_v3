from flask_peewee.rest import RestAPI, UserAuthentication
from psyc import app
#from models.models import Note
import psyc.models.processor as processor
from auth import auth

user_auth = UserAuthentication(auth)
api = RestAPI(app, default_auth=user_auth)
api.register(processor.Processor, processor.ProcessorResource)
api.setup()
