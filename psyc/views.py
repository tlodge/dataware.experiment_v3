from flask import Flask, Markup, url_for, request, make_response, redirect, render_template, flash, session, jsonify
from psyc import app
from psyc.auth import auth
from psyc.models.models import Resource

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
    return render_template('experiment.html', user=user) 

@app.route('/logout')
@auth.login_required
def logout():
    user = auth.logout()
    return redirect('/')
