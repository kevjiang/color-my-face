from flask import Flask, redirect, url_for, session, request
from flask_oauth import OAuth
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
import pdb

SECRET_KEY = 'a398asdifjlk0303*&@$#Jkjkj439*SDKFJ8ou8'
DEBUG = True
FACEBOOK_APP_ID = '1516589151901765'
FACEBOOK_APP_SECRET = '0f41b444386d8bd08005f3d47b6fed26'


app = Flask(__name__)
app.debug = DEBUG
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['KEVIN_DATABASE_URL']
app.secret_key = SECRET_KEY
oauth = OAuth()




class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fbid = db.Column(db.String(100))
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    email = db.Column(db.String(80))
    profile_pic = db.Column(db.String(80))
    def __repr__(self):
        return '#%d: First Name: %s, Last Name: %s, Email: %s, FacebookID: %s, Profile Pic: %s' % (self.id, self.firstname, self.lastname, self.email, self.fbid, self.profile_pic)








facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)


@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <body>

    <h1>My cool app</h1>
    <a href="/login">Login</a>

    </body>
    </html>

    """

@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    # pdb.set_trace()
    if User.query.filter(User.fbid == me.data['id']).first() is None:
        u = User(firstname=me.data['first_name'], lastname=me.data['last_name'], fbid=me.data['id'], email=me.data['email'])
        db.session.add(u)
        db.session.commit()

    return 'Hello %s' %(me.data['name'])


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run()
