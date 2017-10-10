import os
from manage import app as application 

print 'wsgi'

if __name__ == "__main__":
    application.run(host='0.0.0.0')

#user = User.query.filter_by(email=form.email.data).first()
#if user is None:
#    admin = User(email=os.getenv('FLASK_ADMIN'), username='admin', 
#                 password=os.getenv('FLASK_ADMIN_PWD'), confirmed=True)
#    print 'admin user created'