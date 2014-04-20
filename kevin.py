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
    #public information
    fbid = db.Column(db.String(100))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    profile_pic = db.Column(db.String(100))
    gender = db.Column(db.String(20)) #technically onlny needs 1 character

    #needs permissions
    email = db.Column(db.String(100))
    birthday = db.Column(db.String(20)) #technically only needs 10 characters
    political = db.Column(db.String(100))
    rel_status = db.Column(db.String(100))
    religion = db.Column(db.String(100))

    # some attributes that will be harder to get (i.e. not direct field of user node)
    #edu_type = db.Column(db.String(100)) #too complicated b/c multiple "educations" possible
    num_profile_pic = db.Column(db.Integer)
    num_friends = db.Column(db.Integer)
    # languages

    #not yet ready queries
    #edu_type=me.data['education']['type']

    def __repr__(self):
        return '#%d: FacebookID: %s, First Name: %s, Last Name: %s, Profile Pic: %s, Num Profile Pics: %d, Email: %s, Gender: %s, Birthday: %s, Political: %s, Rel Status: %s, Religion: %s, Num Friends: %s' % (self.id, 
            self.fbid, self.firstname, self.lastname, self.profile_pic, self.num_profile_pic, self.email, self.gender, self.birthday, self.political, self.rel_status, self.religion, self.num_friends)

class Photo(db.Model):
    __tablename__ = 'photos'
    # id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(100), primary_key=True)
    # album = db.Column(db.String(100))
    photo_url = db.Column(db.String(100)) #link to album (link)
    created_time = db.Column(db.DateTime(timezone=False)) #(created_time)
    num_likes = db.Column(db.Integer)
    has_caption = db.Column(db.Integer) #1 for true, 0 for false
    # num_tags = db.Column(db.Integer) #number of people tagged in photo
    num_comments = db.Column(db.Integer) #number of comments on photo

    #place 
    #prim_color

    id = db.Column(db.Integer, db.ForeignKey('users.id')) #foreign key to User's id (NOT fbid)
    user = db.relationship("User", backref=db.backref('photos', order_by=id))

    def __repr__(self):
        return '#%s: Photo URL: %s, Likes: %d, Comments: %d' % (self.pid, self.photo_url, self.num_likes, self.num_comments)


facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'user_photos, friends_photos, user_birthday, \
                            user_relationships, user_religion_politics, email'} #this is where you add permissions!
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

    me = facebook.get('/me?fields=id,first_name,last_name,email,gender,birthday,political,relationship_status,religion,name,link,education')
    # userid = me.data['id']
    alb = facebook.get('/me/albums?fields=name,count,type&limit=500')
    albumArray = alb.data['data']

    # frnds = facebook.get('/me/friends?limit=5000')
    # print albumArray

    if User.query.filter(User.fbid == me.data['id']).first() is None:
        #checks to see that all keys exist in dictionary me.data
        #if key doesn't exist, sets field in User row to 'N/A'
        fn=ln=fi=em=ge=bi=po=rs=re='N/A'
        if 'first_name' in me.data:
            fn=me.data['first_name']
        if 'last_name' in me.data:
            ln=me.data['last_name']
        if 'id' in me.data:
            fi=me.data['id']
        if 'email' in me.data:
            em=me.data['email']
        if 'gender' in me.data:
            ge=me.data['gender']
        if 'birthday' in me.data:
            bi=me.data['birthday']
        if 'political' in me.data:
            po=me.data['political']
        if 'relationship_status' in me.data:
            rs=me.data['relationship_status']
        if 'religion' in me.data:
            re=me.data['religion']

        #we use an FQL query b/c it is the only thing that supports friend_count and thus can count all friends
        numFriends = facebook.get('/fql?q=SELECT%20friend_count%20FROM%20user%20WHERE%20uid%20=%20' + me.data['id']).data['data'][0]['friend_count'] 
        

        for item in albumArray:
            #We assume that every user has a Profile Pictures album here
            if (item['name'] == 'Profile Pictures' and item['type'] == 'profile'):
                numPhotos = item['count']

                u = User(firstname=fn, lastname=ln, 
                fbid=fi, email=em, gender=ge, birthday=bi, political=po,
                rel_status=rs, religion=re,
                profile_pic="http://graph.facebook.com/" + me.data['id'] + "/picture?type=square", 
                num_profile_pic=numPhotos, num_friends=numFriends)
                db.session.add(u)

                pho = facebook.get('/' + item['id'] + '/photos?fields=id,album,source,picture,place,link&limit=500')
                photoArray = pho.data['data']

                i=0
                while (i < numPhotos):
                    #getting numLikes
                    lik = facebook.get('/' + photoArray[i]['id'] + '/likes?summary=1')
                    numLikes = 0
                    if 'total_count' in lik.data['summary']:
                        numLikes = lik.data['summary']['total_count']
                    #getting numComments
                    com = facebook.get('/' + photoArray[i]['id'] + '/comments?summary=1')
                    numComments = 0
                    if 'total_count' in com.data['summary']:
                        numComments = com.data['summary']['total_count']

                    p = Photo(pid=photoArray[i]['id'], photo_url=photoArray[i]['link'], num_likes=numLikes,\
                            num_comments=numComments) #change from link to either source or picture later
                    db.session.add(p)
                    i = i+1
                break #we assume that only one Profile Pictures album exists!

        db.session.commit()

    return 'Hello %s! Thank you for participating in our survey.  This is the url of your homepage: %s.' % (me.data['name'], me.data['link']) 

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

if __name__ == '__main__':
    app.run()














# class Album(db.Model):
#     __tablename__ = 'albums'
#     # id = db.Column(db.Integer, primary_key=True)
#     albid = db.Column(db.String(100), primary_key=True)
#     numPhotos = db.Column(db.Integer) #number of photos in album (count)
#     album_url = db.Column(db.String(100)) #link to album (link)
#     # created_time = db.Column(db.DateTime(timezone=False)) #(created_time)

#     id = db.Column(db.Integer, db.ForeignKey('users.id')) #foreign key to User's id (NOT fbid)
#     user = db.relationship("User", backref=db.backref('albums', order_by=id))

#     def __repr__(self):
#         return '#%s: Num Photos: %s, Album URL: %s' % (self.albid, self.numPhotos, self.album_url)


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