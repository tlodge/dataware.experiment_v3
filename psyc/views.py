from gevent import monkey
from flask import Flask, Markup, url_for, request, make_response, redirect, render_template, flash, session, jsonify
monkey.patch_socket()

from flask_peewee.serializer import Serializer, Deserializer
from psyc import app
from psyc.auth import auth
from psyc.models.resource import Resource
from psyc import experimenter
from psyc import updatemanager
import psyc.models.catalog as catalog
import psyc.models.resource as resource
import psyc.models.processor as processor
import psyc.models.execution as execution
import urllib2
import urllib
import json
import datetime
import time
import random
from gevent import getcurrent

um = updatemanager.UpdateManager()

ts        = time.time()
now       = datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d:%H:%M:%S')
aweekago  = datetime.datetime.fromtimestamp(ts-(7*24*60*60)).strftime('%Y/%m/%d:%H:%M:%S')
adayago   = datetime.datetime.fromtimestamp(ts-(24*60*60)).strftime('%Y/%m/%d:%H:%M:%S') 
anhourago = datetime.datetime.fromtimestamp(ts-(60*60)).strftime('%Y/%m/%d:%H:%M:%S')

fakeurls = ["http://www.stackoverflow.com", "http://delicious.com", "http://www.python.org", "http://www.amazon.com", "http://www.bing.com", "http://twitter.bootstrap.com", "http://www.littletechtips.com", "http://forums.devshed.com", "http://support.microsoft.com", "http://howstuffworks.com", "http://en.wikipedia.org"]
    
queries = [ 
            "select ts, url from urls where ts < '%s' and ts > '%s'" % (aweekago,now),
            "select ts, url from urls where ts < '%s' and ts > '%s'" % (adayago,now),
            "select ts, url from urls where ts < '%s' and ts > '%s'" % (anhourago,now)
          ]
           
@app.route('/')
def root():
    return render_template('home.html')

@app.route('/register', methods=['POST'])
def register():
   
   username     = request.form['username']
   password     = request.form['password']
   email        = request.form['email']
   catalog_uri  = request.form['catalog_uri']
   owner        = request.form['catalog_name']
   
   #create the new user
   user = auth.User(username=username, email=email, admin=False, active=True)
   user.set_password(password)
   user.save()
   auth.login_user(user) 
   print "successfully logged in the user"
   
   #create the users resource
   resource = Resource(user=user, catalog_uri=catalog_uri, owner=owner, resource_name='urls')
   
   print "created the resource!!"
   
   #fetch the resource uri from the catalog
   cat = catalog.fetch_by_uri(catalog_uri)
   
   
   
   if cat is not None:
        print "got the resource uri from the catalog!" 
        data = experimenter.fetch_resource(cat, owner, 'urls')
        print "data is %s" % data
        
        res = json.loads(data)
        
        if len(res) > 0:
            print "got"
            print res
            print "resource_uri %s" % res[0]['resource_uri']
            resource.resource_uri = res[0]['resource_uri']
    
   resource.save()
   return redirect('/experiment/')   


@app.route('/experiment/')
@auth.login_required
def experiment():
    user = auth.get_logged_in_user()
   
    questions = [
        {
            "id": "%d_1" % user.id, 
            "link": "question one", 
            "title": "last 7 days  worth of browsing", 
            "description": "On the left hand side is a selection of some of the urls that you visited in the last 7 days...the question is.....",
            "query": queries[0]
        },
        {
            "id": "%d_2" % user.id,
            "link": "question two", 
            "title": "last 24 hour's browsing", 
            "description":"On the left hand side is a selection of some of the urls that you visited in the last 24 HOURS...the question is.....",
            "query": queries[1]
        },
        {   
            "id": "%d_3" % user.id,
            "link": "question three", 
            "title": "last hour's worth of browsing", 
            "description": "On the left hand side is a selection of some of the urls that you visited in THE LAST HOUR!...the question is.....",
            "query": queries[2]
        }
    ]

        
    if user.admin:
      return redirect('/admin/')
    
    myresource = resource.fetch_by_user(user)
    
    if myresource is not None:
       mycatalog = catalog.fetch_by_uri(myresource.catalog_uri)
       processors = processor.fetch_by_resource(myresource)
       
       data = _mash(execution.fetch_results_for_user(user))
       
       #print "adta is"
       print data
       if processors is None:
            experimenter.register_processor(mycatalog, myresource)
            processors = processor.fetch_by_resource(myresource)
    
       return render_template('experiment.html', user=user, catalog="%s/%s" % (mycatalog.uri, 'audit'), processors=processors, questions=questions, results=json.dumps(data)) 
    
    else:
       return "You don't seem to have a resource"

def _mash(results):
    
    #first, add in an 'auth' field to differentiate between authentic / fake urls
    for key in results:
        values = results[key]
        newlist = []
    
        for data in json.loads(values):
            data['auth'] = True
            newlist.append(data)
            
            if random.random() >= 0.6:
                ts = int(datetime.datetime.strptime(data['ts'], '%Y/%m/%d:%H:%M:%S').strftime("%s"))
                ts += 60 * 2
                newlist.append({'ts' : datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d:%H:%M:%S'), 'url':  fakeurls[random.randint(0,len(fakeurls)-1)], 'auth':False})
                print "%s %s" %  (data['ts'],  datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d:%H:%M:%S'))
            
        results[key] = json.dumps(newlist)
        
    return results
 
@app.route( '/stream')
@auth.login_required
def stream():
    
    user = auth.get_logged_in_user()
    timeout       = time.time() + 15
    
    #alternatively could add a snum to each event, and have the um.event.wait timeout
    #and send if event snum > mysnum
    
    while time.time() < timeout:
        try:
            um.event.wait()
            message = um.latest()
            
            print "*** %s ****seen a new message! %d %d" % (id(getcurrent()), user.id, message['user_id'])
            
            if user.id == message['user_id']:
                print "%d: sending message" % user.id
                jsonmsg = json.dumps(message)
                return jsonmsg
        
        except Exception, e:
            print "exception!"      
            return json.dumps({'type':'error', 'data':e})
   
    print "TIMED OUT"
    return json.dumps({'type':'error', 'data':'timeout'})
    
@app.route('/logout')
@auth.login_required
def logout():
    user = auth.logout()
    return redirect('/')

@app.route('/serialize')
def serialize():
    user = auth.get_logged_in_user()    
    myresource = resource.fetch_by_user(user)
    return json.dumps(Serializer().serialize_object(myresource))
    
           
@app.route('/processor')
def token():

    error = request.args.get('error', None)
    state =  request.args.get('state', None)

    if not(error is None):
        app.logger.info(error)
        app.logger.info(request.args.get('error_description', None))
        prec = processor.updateProcessorRequest(state=state, status=error)
        
        um.trigger({    
            "type": "resource",
            "message": "a resource request has been rejected",
            "user_id" : prec.resource.user.id,
            "data": json.dumps(Serializer().serialize_object(prec))                  
        });
        
        return "Noted rejection <a href='%s/audit'>return to catalog</a>" % prec.catalog.uri

    code  =  request.args.get('code', None)

    prec = processor.updateProcessorRequest(state=state, status="accepted", code=code)

    if prec is not None:
        url = '%s/client_access?grant_type=authorization_code&redirect_uri=%s&code=%s' % (prec.catalog.uri, prec.catalog.redirect_uri,code)
        f = urllib2.urlopen(url)
        data = f.read()
        f.close()
        result = json.loads(data.replace( '\r\n','\n' ), strict=False)

        if result["success"]:
           prec = processor.updateProcessorRequest(state=state, status="accepted", token=result["access_token"])
           
           um.trigger({    
                "type": "resource",
                "message": "a resource request has been accepted",
                "user_id":prec.resource.user.id,
                "data": json.dumps(Serializer().serialize_object(prec))              
           });
           
           experimenter.perform_execution(prec, "%d_1" % prec.resource.user.id, '["%s","%s"]' % (aweekago,now))
           experimenter.perform_execution(prec, "%d_2" % prec.resource.user.id, '["%s","%s"]' % (adayago,now))
           experimenter.perform_execution(prec, "%d_3" % prec.resource.user.id, '["%s","%s"]' % (anhourago,now))
              
           return "Successfully obtained token <a href='/experiment'>return to experiment</a>"
	       
	       #return redirect('/experiment')
        else:
           return  "Failed to swap auth code for token <a href='%s/audit'>return to catalog</a>" % prec.catalog.uri

    return "No pending request found for state %s" % state  
 
@app.route( '/trigger/<execution_id>')
def trigger(execution_id):
    
    print "triggering for executionid %s" % execution_id
    
    myex = execution.fetch_by_id(execution_id=execution_id)
        
    um.trigger({    
        "type": "execution",
        "message": "results have been received from an execution %d" % random.randint(0,500),
        "user_id":myex.user.id,
        "data": myex.result              
    });
    
    return "thanks!"
    
@app.route('/result/<execution_id>', methods=['POST'])
def result(execution_id):

    success = True
    
    print "got results for execution id %s" % execution_id
    
    try:
        if (request.form['success'] == 'True'):
            print "success is true!"
            
            result = request.form['return']
            
            print "results are %s" % result
            print "saving execution"
            my_execution = execution.update(execution_id=execution_id, result=str(result))
            print "saved execution"
            
            um.trigger({    
                "type": "execution",
                "message": "results have been received from an execution",
                "user_id":my_execution.user.id,
                "data": my_execution.result              
            });
        
        else:
            print "not doing anything at the mo!"

    except:
        print "failed to store results"
        success = False

    return json.dumps({'success':success})
