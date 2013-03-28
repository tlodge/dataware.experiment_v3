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
  uri = CharField()
  client_id = CharField()
  redirect_uri = CharField()
  registered = DateTimeField(default=datetime.datetime.now) 

class CatalogAdmin(ModelAdmin):
  columns = ('uri', 'client_id', 'redirect_uri', 'registered')

def fetch_by_uri(uri):
  try:
    return Catalog.get(Catalog.uri == uri)
  except Catalog.DoesNotExist:
    return None  

def register():

   catalog_uri    = "http://192.168.33.10:5000"
 
   #check if already registered with the catalog
   if fetch_by_uri(catalog_uri) is not None:
     return

   url = "%s/client_register" % catalog_uri

   redirect_uri = "%s/%s" % (REALM, "processor") 

   values = {
         'redirect_uri': redirect_uri,
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
   print result

   if (result['success']):
      insert_registration(catalog_uri, result['client_id'], redirect_uri)

def insert_registration(uri, client_id, redirect_uri):
   catalog = Catalog(uri=uri, client_id=client_id, redirect_uri=redirect_uri)
   catalog.save()
