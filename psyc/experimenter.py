import time
import urllib2
import urllib
import hashlib
import json
from psyc.models.processor import Processor 
import psyc.models.execution as execution

REALM  = "http://192.168.33.33:9080"

def fetch_resource(catalog, owner, resource):
    url = "%s/client_list_resources?client_id=%s&client_uri=%s&resource_owner=%s&resource_name=%s" % (catalog.uri, catalog.client_id, catalog.redirect_uri, owner, resource) 
    f = urllib2.urlopen(url)
    data = f.read()  
    f.close()
    return data
    
def register_processor(catalog, resource, query):
  
  print "in register processor!"
  
  #set expiry to two hours from now
  expiry = time.time() + (60 * 60 * 2)  
  
  state = "%d" % time.time()

  values = {
            'client_id': catalog.client_id,
            'state': state,
            'redirect_uri': catalog.redirect_uri,
            'scope': '{"resource_name" : "%s", "expiry_time": %s, "query": "%s"}' % (resource.resource_name,expiry,query)
  }

  url = "%s/user/%s/client_request" % (catalog.uri,resource.owner)
 
  print "url is %s" % url
  data = urllib.urlencode(values)
  req = urllib2.Request(url,data)
  response = urllib2.urlopen(req)
  result = response.read()
  
  result = json.loads(
        result.replace( '\r\n','\n' ),
        strict=False
  )

  if (not(result['success'])):
     return False
    
  proc = Processor(state=state, catalog=catalog, resource=resource, expiry=expiry, query=query)
  proc.save()
  return True 

def perform_execution(processor,parameters):
  
  if not(processor is None):
  
     url = '%s/invoke_processor' % processor.resource.resource_uri
     m = hashlib.md5()
     m.update('%f' % time.time())
     id = m.hexdigest()

     values = {
        'access_token':processor.token,
        'parameters': parameters,
        'result_url' : "%s/result/%s" % (REALM,id)
     }

     data = urllib.urlencode(values)
     req = urllib2.Request(url,data)
     response = urllib2.urlopen(req)
     data = response.read()

     result = json.loads(data.replace( '\r\n','\n' ), strict=False)

     execution.add(execution_id=id, access_token=processor.token, parameters=parameters)

