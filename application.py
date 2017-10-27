from models import Base, User, Item, Category
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, g
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask.ext.httpauth import HTTPBasicAuth
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests
import random
import string
from functools import wraps
from flask import session as login_session


auth = HTTPBasicAuth()


engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# auth code
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# login Oauth Call function
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    # Upgrade the authorization code into a credentials object
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        print 1
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        print 2
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        print 3
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print "Response from Google..."
    print data

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # See if user exists
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    return "Login Successful"


@app.route('/logout')
def logout():
    gdisconnect()
    del login_session['gplus_id']
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']

    return redirect(url_for('homepage'))


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')

    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# homepage
@app.route('/')
def homepage():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('publicHome.html', categories=categories)

    else:
        return render_template('home.html', categories=categories)


# show Category
@app.route('/category/<int:category_id>')
def showCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    if 'username' not in login_session:
        return render_template(
            'publicCategory.html', items=items, category=category)
    else:
        return render_template(
            'category.html', items=items, category=category)


# create Category
@app.route('/category/create', methods=['GET', 'POST'])
def createCategory():
    # check for login
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('homepage'))
    else:
        return render_template('newCategory.html')


# edit Category
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    # check for login
    if 'username' not in login_session:
        return redirect('/login')

    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            return redirect(url_for('homepage'))
    else:
        return render_template(
            'editCategory.html', category=editedCategory)


# delete Category
@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    # check for login
    if 'username' not in login_session:
        return redirect('/login')

    deletedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(deletedCategory)
        session.commit()
        return redirect(
            url_for('homepage'))
    else:
        return render_template(
            'deleteCategory.html', category=deletedCategory)


# add Item
@app.route('/category/<int:category_id>/item/add', methods=['GET', 'POST'])
def newItem(category_id):
    # check for login
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form[
            'description'], price=request.form['price'],
            category_id=category_id)
        session.add(newItem)
        session.commit()

        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('addItem.html', category_id=category_id)

    return render_template('addItem.html', category=category)


# delete Item
@app.route('/category/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    # see if user logged in
    if 'username' not in login_session:
        return redirect('/login')

    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    user = getUserInfo(Item.user_id)

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


# edit Item
@app.route('/category/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    # see if user logged in
    if 'username' not in login_session:
        return redirect('/login')

    editedItem = session.query(Item).filter_by(id=item_id).one()
    user = getUserInfo(Item.user_id)

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['name']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showCategory', category_id=category_id))
    else:

        return render_template(
            'updateItem.html', category_id=category_id, item_id=item_id,
            item=editedItem)


# API Calls
@app.route('/category/<int:category_id>/JSON')
def categoryItemsJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super-secret-key'
    app.run(host='0.0.0.0', port=8000)
