from flask import Flask

#config the database
DEBUG = True
SECRET_KEY = 'sssssshhuuuuushshsh'
DATABASE = {
        'name' : 'psyc.db',
        'engine': 'peewee.SqliteDatabase',
}
app = Flask(__name__)
app.config.from_object(__name__)
