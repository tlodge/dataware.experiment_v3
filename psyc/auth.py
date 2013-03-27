from psyc import database
from psyc import app
from flask_peewee.auth import Auth
auth = Auth(app, database.db)
