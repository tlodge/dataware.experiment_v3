import time
import urllib2
import urllib
import hashlib
import json
from psyc.models.processor import Processor 

def register_processor(catalog, resource, query):

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

def perform_execution(state,parameters,processor,result_url):
  if not(processor is None):
     url = '%s/invoke_processor' % processor.resource_uri
     m = hashlib.md5()
     m.update('%f' % time.time())
     id = m.hexdigest()

     values = {
        'access_token':processor.token,
        'parameters': parameters,
        #'result_url' : "%s/result/%s" % (REALM,id)
     }

     data = urllib.urlencode(values)
     req = urllib2.Request(url,data)
     response = urllib2.urlopen(req)
     data = response.read()

     result = json.loads(data.replace( '\r\n','\n' ), strict=False)

     #addExecutionRequest(execution_id=id, access_token=processor.token, parameters=parameters, sent=int(time.time()))
