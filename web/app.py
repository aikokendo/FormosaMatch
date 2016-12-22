# app.py

"""#!/usr/bin/env python"""
""" application file """
from flask import Flask
from flask import request, redirect, session, abort, url_for, render_template
# from models import queries, user, language
from models import queries, user
from py2neo import Graph

app = Flask(__name__)
app.config['DEBUG'] = True

graph = Graph('http://neo4j:neo4j@192.168.99.100:7474/db/data/')

@app.route('/', methods=['GET', 'POST'])
def index():
    """ index handler """
    #users = queries.get_users(graph)
    return render_template('index.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#         """ register handler """
#     error = None
#     if request.method == 'POST':
#         email = request.form['email']
#         username = request.form['username']
#         password = request.form['password']
#         if len(email) < 1:
#             error = 'You must give us an email.'
#         elif len(password) < 5:
#             error = 'Your password must be at least 5 characters.'
#         elif not user.User(graph=graph, email=email, username=username).register(password):
#             error = 'A user with that email already exists.'
#         else:
#             session['email'] = email
#             session['username'] = username
#             return redirect(url_for('index'))
#
#     # return render_template('register.html', error=error)
#     return render_template('index.html', error=error)
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """ login handler """
#     error = None
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         if not user.User(graph=graph, email=email).verify_password(password):
#             if not user.User(graph=graph, username=email).verify_password(password):
#                 error = 'Invalid login.'
#         if error ==  None:
#             _user = user.User(graph=graph, email=email).find()
#             if _user == None:
#                 _user = user.User(graph=graph, username=email).find()
#             session['email'] = email
#             session['username'] = _user['username']
#             return redirect(url_for('index'))
#     # return render_template('login.html', error=error)
#     return render_template('index.html', error=error)
#
# @app.route('/logout')
# def logout():
#     """ logout handler """
#     session.pop('email', None)
#     session.pop('username', None)
#     return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
