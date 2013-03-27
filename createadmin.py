from psyc.auth import auth
admin = auth.User(username="admin", email='tlodge@gmail.com', admin=True, active=True)
admin.set_password("admin")
admin.save()
