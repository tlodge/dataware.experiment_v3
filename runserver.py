from psyc import app
from psyc.auth import auth
from psyc import database
from psyc.models.models import Url, UrlAdmin, Resource, ResourceAdmin
import psyc.models.catalog as catalog
from flask_peewee.admin import Admin
port = 9080

auth.User.create_table(fail_silently=True)
Url.create_table(fail_silently=True)
Resource.create_table(fail_silently=True)
catalog.Catalog.create_table(fail_silently=True)

admin = Admin(app,auth)
auth.register_admin(admin)
admin.register(Url, UrlAdmin)
admin.register(Resource, ResourceAdmin)
admin.register(catalog.Catalog, catalog.CatalogAdmin)
admin.setup()

import psyc.rest
import psyc.views
catalog.register()
app.run(host='0.0.0.0', port=port, debug=True)

