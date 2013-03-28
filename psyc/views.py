from flask import Flask, Markup, url_for, request, make_response, redirect, render_template, flash, session, jsonify
from psyc import app
from psyc.auth import auth
from psyc.models.resource import Resource
from psyc import experimenter
import psyc.models.catalog as catalog
import psyc.models.resource as resource
import psyc.models.processor as processor
import urllib2
import urllib
import json

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
   resource.save()
   return redirect('/special/')   

@app.route('/experiment/')
@auth.login_required
def experiment():
    user = auth.get_logged_in_user()

    myresource = resource.fetch_by_user(user)
    mycatalog = catalog.fetch_by_uri(myresource.catalog_uri)
    query = "select * from %s LIMIT 191" % myresource.resource_name
    experimenter.register_processor(mycatalog, myresource, query)
    return render_template('experiment.html', user=user) 

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
  
           experimenter.perform_execution(proc,"[]",result_url):

	   return "Successfully obtained token <a href='%s/audit'>return to catalog</a>" % prec.catalog.uri
        else:
           return  "Failed to swap auth code for token <a href='%s/audit'>return to catalog</a>" % prec.catalog.uri

    return "No pending request found for state %s" % state

@app.route('/result/<execution_id>', methods=['POST'])
def result(execution_id):

    success = True

    try:
        if (request.form['success'] == 'True'):
	    execution.update(execution_id=execution_id, result=str(result), received=int(time.time()))
        else:
            print "not doing anything at the mo!"

    except:
        success = False

    return json.dumps({'success':success})
