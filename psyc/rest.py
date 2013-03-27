from flask_peewee.rest import RestAPI, UserAuthentication
from psyc import app
#from models.models import Note
from auth import auth

user_auth = UserAuthentication(auth)
api = RestAPI(app, default_auth=user_auth)
#api.register(Note)
api.setup()
