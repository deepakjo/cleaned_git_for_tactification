"""
App starts from this file. It creates all the global code
and also setting config environment.
"""
#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Post, Comment
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail

app = create_app(os.getenv('FLASK_CONFIG') or 'development')
manager = Manager(app)
migrate = Migrate(app, db)         

####Code coverage
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

#def get_resource_as_string(name, charset='utf-8'):
#    with app.open_resource(name) as f:
#        return f.read().decode(charset)

#app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

#pg70 Creating Mail account.
mail = Mail(app)

def make_shell_context():
    """
    Shell context init'd here.
    """
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Comment=Comment)

@manager.command
def test(coverage=False):
    """Run the Unit Tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover('selenium')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        print ('Base dir:', basedir)
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

def delete():
    """
    From shell context delete all users from db
    """
    user = User.query.all()
    for ent in user:
        db.session.delete(ent)
    db.session.commit()

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
        manager.run()
