from flask import Flask, redirect, url_for, session, request
from flask_oauth import OAuth
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.sqlalchemy import relationship, backref
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
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    profile_pic = db.Column(db.String(100))
    def __repr__(self):
        return '#%d: First Name: %s, Last Name: %s, Email: %s, FacebookID: %s, Profile Pic: %s' % (self.id, self.firstname, self.lastname, self.email, self.fbid, self.profile_pic)

class Album(db.Model):
    __tablename__ = 'albums'
    # id = db.Column(db.Integer, primary_key=True)
    albid = db.Column(db.String(100), primary_key=True)
    numPhotos = db.Column(db.Integer) #number of photos in album (count)
    album_url = db.Column(db.String(100)) #link to album (link)
    # created_time = db.Column(db.DateTime(timezone=False)) #(created_time)

    id = db.Column(db.Integer, db.ForeignKey('users.id')) #foreign key to User's id (NOT fbid)
    user = db.relationship("User", backref=db.backref('albums', order_by=id))

    def __repr__(self):
        return '#%s: Num Photos: %s, Album URL: %s' % (self.albid, self.numPhotos, self.album_url)

class Photo(db.Model):
    __tablename__ = 'photos'
    # id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(100), primary_key=True)
    # album = db.Column(db.String(100))
    photo_url = db.Column(db.String(100)) #link to album (link)
    # created_time = db.Column(db.DateTime(timezone=False)) #(created_time)

    id = db.Column(db.Integer, db.ForeignKey('users.id')) #foreign key to User's id (NOT fbid)
    user = db.relationship("User", backref=db.backref('photos', order_by=id))

    def __repr__(self):
        return '#%s: Photo URL: %s' % (self.pid, self.photo_url)


facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email, user_photos, friends_photos'} #this is where you add permissions!
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
    # return(render_template('home.html'))

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
    # userid = me.data['id']
    alb = facebook.get('/me/albums?fields=name,count&limit=500')
    albumArray = alb.data['data']
    # print albumArray

    if User.query.filter(User.fbid == me.data['id']).first() is None:
        u = User(firstname=me.data['first_name'], lastname=me.data['last_name'], fbid=me.data['id'], email=me.data['email'], profile_pic="http://graph.facebook.com/" + me.data['id'] + "/picture?type=square")
        db.session.add(u)

        #find profile picture album id

        for item in albumArray:
            if (item['name'] == 'Profile Pictures'):
                numPhotos = item['count']
                pho = facebook.get('/' + item['id'] + '/photos?fields=id,album,source,picture,place,link&limit=500')
                photoArray = pho.data['data']
                print photoArray
                print numPhotos
                i = 0
                while (i < numPhotos):
                    p = Photo(pid=photoArray[i]['id'], photo_url=photoArray[i]['link']) #change from link to either source or picture later
                    db.session.add(p)
                    i = i+1

        db.session.commit()

    return 'Hello %s! This is a link to your homepage: %s.' % (me.data['name'], me.data['link']) 

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

if __name__ == '__main__':
    app.run()
















    # phot = facebook.get('/me/photos?fields=id,album,source,picture,place,link&limit=500')
    # photoArray = phot.data['data']    #[0]['album']['name']
    #data[0]['id']
    # print photoArray
    # pdb.set_trace()

        # albcount = 0
        # totcount = 0
        # for item in photoArray:
        #     totcount = totcount + 1
        #     print item
        #     if 'album' in item:
        #         if (item['album']['name'] == 'Profile Pictures'):
        #             albcount = albcount + 1
        #             p = Photo(pid=item['id'], album=item['album']['name'], photo_url=item['link'])
        #             db.session.add(p)

        # print 'number of photos with album name = ' + str(albcount)
        # print 'tot number of photos = ' + str(totcount)

        # for item in photoArray:
            # print item
            # if (item['album'] == 'Profile Picture'): #only add picture to database if in Profile Picture album
            #     p = Photo(pid=item['id'], album=item['album'], photo_url=item['link'])
            #     db.session.add(p)

        # albumArray = alb.data
        # for item in albumArray:
        #     print item
        #     if (item.data['name'] == "Profile Pictures" and item.data['type'] == 'profile'):
        #         a = Album(albid=item.data['id'], numPhotos=item.data['count'], albulm_url=item.data['picture']) #or try source instead of picture for bigger image
        #         db.session.add(a)
