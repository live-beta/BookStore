#!/usr/bin/env python

import os
from app import create_app, db, api
from app.stock.models import User,Books
from app.stock.views import LoginUser, RegisterUser, BookStockAction
from flask_script import Manager, Shell, prompt_bool
from flask_migrate import Migrate, MigrateCommand
from flask import jsonify
from flask import Flask, render_template
from app.users.user_auth import token_auth, g
import coverage

COV = coverage.coverage(
    branch=True,
    include='app/*',
    omit=[
        'app/models.py',
        'app/__init__.py',
        'app/utils.py',

    ]
)
COV.start()

# creting Flask application from app factory
app = create_app(os.getenv('FLASK_CONFIG')or 'default')

# Initalising the member class

manager = Manager(app)

# initialising the migrate clas
migrate = Migrate(app, db)

# make custom json error codes

@app.route('/')
def index():
    decorators = [token_auth.login_required]

    return render_template('index.html')
   

   

@app.errorhandler(500)
def server_error(e):
    return jsonify(error=500, message=str(e)), 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404Error.html')
    return jsonify(error=404, message=str(e)), 404



def make_shell_context():
    """ Imports modules into shell"""
    return dict(app=app, db=db, User=User, Bucketlist=Bucketlist, Item=Item)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """For running Unit tests"""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    COV.stop()
    COV.save()
    print('Coverage summay from the tests')
    COV.report()
    COV.html_report()
    COV.erase()
    return 0


@manager.command
def dropdb():
    """ Deletes database data, destroying all the tables that have been created"""
    if prompt_bool("This operation will delete your data irreversably,\
                are you sure you want to proceed with the operation?"):
        db.drop_all()
        print("All the data has been deleted")


if __name__ == "__main__":
    api.add_resource(LoginUser, "/auth/login", endpoint="token")
    api.add_resource(RegisterUser, "/auth/register", endpoint="register")
    api.add_resource(BookStockAction, "/books",
                     "/books/<book_idbm>", endpoint="book")

    
    # api.add_resource(ItemAction, "/bucketlists/<id>/items",
    #                  "/bucketlists/<id>/items/<Item_id>", endpoint="items")
    manager.run()
