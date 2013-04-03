from flask import Flask, Markup, url_for, request, make_response, redirect, render_template, flash, session, jsonify
from psyc import app
from psyc.auth import auth
from psyc.models.resource import Resource
from psyc import experimenter
import psyc.models.catalog as catalog
import psyc.models.resource as resource
import psyc.models.processor as processor
import psyc.models.execution as execution
import urllib2
import urllib
import json
import datetime

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
   #create the users resource
   resource = Resource(user=user, catalog_uri=catalog_uri, owner=owner, resource_name='urls')
   cat = catalog.fetch_by_uri(catalog_uri)
   
   if cat is not None:
        data = experimenter.fetch_resource(cat, owner, 'urls')
        res = json.loads(data)
        if len(res) > 0:
            print "resource_uri %s" % res[0]['resource_uri']
            resource.resource_uri = res[0]['resource_uri']
    
   resource.save()
   return redirect('/experiment/')   

@app.route('/getdetails/')
@auth.login_required
def getdetails():
   cat = catalog.fetch_by_uri("http://192.168.33.10:5000")
   
   if cat is not None:
        data = experimenter.fetch_resource(cat, 'yahootom', 'urls')
        res = json.loads(data)
        print res
        return res[0]['resource_uri']
   
   return "nowt"

@app.route('/experiment/')
@auth.login_required
def experiment():
    user = auth.get_logged_in_user()
    
    if user.admin:
      return redirect('/admin/')
    
    myresource = resource.fetch_by_user(user)
    
    if myresource is not None:
       mycatalog = catalog.fetch_by_uri(myresource.catalog_uri)
       processors = processor.fetch_by_resource(myresource)
       
       if processors is None:
            print "registering a new processor!"
            query = "select * from %s LIMIT 210" % myresource.resource_name
            experimenter.register_processor(mycatalog, myresource, query)
            processors = processor.fetch_by_resource(myresource)
       
       print "ahahah got processors"
       print processors
       
       return render_template('experiment.html', user=user, catalog="%s/%s" % (mycatalog.uri, 'audit'), processors=processors) 
    
    else:
       return "You don't seem to have a resource"

@app.route('/logout')
@auth.login_required
def logout():
    user = auth.logout()
    return redirect('/')

@app.route('/processor')
def token():

    error = request.args.get('error', None)
    state =  request.args.get('state', None)

    if not(error is None):
        app.logger.info(error)
        app.logger.info(request.args.get('error_description', None))
        prec = processor.updateProcessorRequest(state=state, status=error)
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
           experimenter.perform_execution(prec,"[]")
	   return "Successfully obtained token <a href='%s/audit'>return to catalog</a>" % prec.catalog.uri
        else:
           return  "Failed to swap auth code for token <a href='%s/audit'>return to catalog</a>" % prec.catalog.uri

    return "No pending request found for state %s" % state

@app.route('/result/<execution_id>', methods=['POST'])
def result(execution_id):

    success = True

    try:
        if (request.form['success'] == 'True'):
            result = request.form['return']
	    execution.update(execution_id=execution_id, result=str(result))
        else:
            print "not doing anything at the mo!"

    except:
        print "failed to store results"
        success = False

    return json.dumps({'success':success})
