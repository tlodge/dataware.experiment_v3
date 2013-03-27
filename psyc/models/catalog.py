import datetime
import json
from flask_peewee.admin import Admin, ModelAdmin
from psyc.auth import auth
from psyc.database import db
from peewee import *
import urllib2
import urllib

CLIENTNAME = "psycho"
REALM      = "http://192.168.33.33:9080"

class Catalog(db.Model):
  uri = TextField()
  registered = DateTimeField(default=datetime.datetime.now) 

class CatalogAdmin(ModelAdmin):
  columns = ('uri', 'registered')

def register():

   catalog_uri    = "http://192.168.33.10:5000"

   if registered(catalog_uri):
     return

   url = "%s/client_register" % catalog_uri

   values = {
         'redirect_uri': "%s/%s" % (REALM, "processor"),
         'client_name':CLIENTNAME
   }

   data = urllib.urlencode(values)
   req = urllib2.Request(url,data)
   response = urllib2.urlopen(req)
   result = response.read()
   result = json.loads(
      result.replace( '\r\n','\n' ),
      strict=False
   )

   if (result['success']):
      insert_registration(catalog_uri)

def registered(catalog_uri):
  try: 
    Catalog.get(Catalog.uri == catalog_uri) is not None
    return True
  except Catalog.DoesNotExist:
    return False

def insert_registration(uri):
   catalog = Catalog(uri=uri)
   catalog.save()
