import createadmin

import psyc.models.catalog as catalog
import psyc.models.url as url
import psyc.models.resource as resource

from psyc.auth import auth

user1 = auth.User(username="user1", email='user1@dataware.com', admin=False, active=True)
user1.set_password("user1")
user1.save()

user2 = auth.User(username="user2", email='user2@dataware.com', admin=False, active=True)
user2.set_password("user2")
user2.save()

res = resource.Resource(user=user1, catalog_uri='http://192.168.33.10:5000', owner='tlodge', resource_name='urls') 
res.save()

testurl  = url.Url(user=user1, ts=1234456789, macaddr='aa:bb:cc:dd:ee:ff', ipaddr='192.168.22.33', url='http://www.google.com')
testurl.save()

