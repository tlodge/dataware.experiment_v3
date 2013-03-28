from psyc import app
from psyc.auth import auth
from psyc import database

import psyc.models.catalog as catalog
import psyc.models.url as url
import psyc.models.resource as resource
import psyc.models.processor as processor
import psyc.models.execution as execution

from flask_peewee.admin import Admin
port = 9080

auth.User.create_table(fail_silently=True)

url.Url.create_table(fail_silently=True)
resource.Resource.create_table(fail_silently=True)
catalog.Catalog.create_table(fail_silently=True)
processor.Processor.create_table(fail_silently=True)
execution.Execution.create_table(fail_silently=True)

admin = Admin(app,auth)
auth.register_admin(admin)

admin.register(url.Url, url.UrlAdmin)
admin.register(resource.Resource, resource.ResourceAdmin)
admin.register(catalog.Catalog, catalog.CatalogAdmin)
admin.register(processor.Processor, processor.ProcessorAdmin)
admin.register(execution.Execution, execution.ExecutionAdmin)

admin.setup()

import psyc.rest
import psyc.views
catalog.register()
app.run(host='0.0.0.0', port=port, debug=True)

