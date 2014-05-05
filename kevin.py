from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth, OAuthException
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template
import os
import pdb

import struct
from PIL import Image
import scipy
import scipy.misc
import scipy.cluster
from StringIO import StringIO
import urllib2 as urllib


SECRET_KEY = 'a398asdifjlk0303*&@$#Jkjkj439*SDKFJ8ou8'
DEBUG = True
FACEBOOK_APP_ID = '1516589151901765'
FACEBOOK_APP_SECRET = '0f41b444386d8bd08005f3d47b6fed26'


app = Flask(__name__)
app.debug = DEBUG
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['KEVIN_DATABASE_URL']
app.secret_key = SECRET_KEY
oauth = OAuth(app)

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

    photos = db.relationship('Photo', backref='user', lazy='dynamic')

    #not yet ready queries
    #edu_type=me.data['education']['type']

    def __repr__(self):
        return '#%d: FacebookID: %s, First Name: %s, Last Name: %s, Profile Pic: %s, Num Profile Pics: %d, Email: %s, Gender: %s, Birthday: %s, Political: %s, Rel Status: %s, Religion: %s, Num Friends: %s' % (self.id, 
            self.fbid, self.firstname, self.lastname, self.profile_pic, self.num_profile_pic, self.email, self.gender, self.birthday, self.political, self.rel_status, self.religion, self.num_friends)

class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(1000))
    # album = db.Column(db.String(100))
    photo_url = db.Column(db.String(1000)) #link to album (link)
    created_time = db.Column(db.String(100)) #(created_time)
    num_likes = db.Column(db.Integer)
    # has_caption = db.Column(db.Integer) #1 for true, 0 for false
    # num_tags = db.Column(db.Integer) #number of people tagged in photo
    num_comments = db.Column(db.Integer) #number of comments on photo
    red = db.Column(db.String(100))
    green = db.Column(db.String(100))
    blue = db.Column(db.String(100))
    true_color = db.Column(db.String(100))
    prom_color = db.Column(db.String(100))
    sat = db.Column(db.String(100))
    light = db.Column(db.String(100))

    #place 
    #prim_color

    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) #foreign key to User's id (NOT fbid)

    def __repr__(self):
        return '#%d: Photo ID: %sPhoto URL: %s, Likes: %d, Comments: %d, Created Time: %s, Red: %s, Green: %s, Blue: %s, True_Color: %s, Prom_Color: %s, Saturation: %s, Lightness: %s, Userid: %s' % (self.id, self.pid, self.photo_url, self.num_likes, self.num_comments, self.created_time, self.red, self.green, self.blue, self.true_color, self.prom_color, self.sat, self.light, self.user_id)


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
    # return """
    # <!DOCTYPE html>
    # <html>
    # <body>

    # <h1>My cool app</h1>
    # <a href="/login">Login</a>

    # </body>
    # </html>
    # """
    return(render_template('home.html'))

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

                rgbColor = {
                    #reds
                    'maroon': [128, 0, 0],
                    'dark red': [139, 0, 0],
                    'firebrick': [178, 34, 34],
                    'crimson': [220, 20, 60],
                    'red': [255, 0, 0],
                    'tomato': [255, 99, 71],
                    'indian red': [205, 92, 92],
                    'light coral': [240, 128, 128],
                    #oranges
                    'coral': [255, 127, 80],
                    'dark salmon': [233, 150, 122],
                    'salmon': [250, 128, 114],
                    'light salmon': [255, 160, 122],
                    'orange red': [255, 69, 0],
                    'dark orange': [255, 140, 0],
                    'orange': [255, 165, 0],
                    #yellows
                    'gold': [255, 215, 0],
                    'golden rod': [218, 165, 32],
                    'yellow': [255, 255, 0],
                    'corn silk': [255, 248, 220],
                    'lemon chiffon': [255, 250, 205],
                    'light golden rod yellow': [250, 250, 210],
                    'light yellow': [255, 255, 224],
                    #browns
                    'brown': [165, 42, 42],
                    'dark golden rod': [184, 134, 11],
                    'pale golden rod': [238, 232, 170],
                    'dark khaki': [189, 183, 107],
                    'khaki': [240, 230, 140],
                    'saddle brown': [139, 69, 19],
                    'sienna': [160, 82, 45],
                    'chocolate': [210, 105, 30],
                    'sandy brown': [244, 164, 96],
                    'burly wood': [222, 184, 135],
                    'tan': [210, 180, 140],
                    'rosy brown': [188, 143, 143],
                    #greens
                    'olive': [128, 128, 0],
                    'yellow green': [154, 205, 50],
                    'dark olive green': [85, 107, 47],
                    'olive drab': [107, 142, 35],
                    'lawn green': [124, 252, 0],
                    'chart reuse': [127, 255, 0],
                    'green yellow': [173, 255, 47],
                    'dark green': [0, 100, 0],
                    'green': [0, 128, 0],
                    'forest green': [34, 139, 34],
                    'lime': [0, 255, 0],
                    'lime green': [50, 205, 50],
                    'light green': [144, 238, 144],
                    'pale green': [152, 251, 152],
                    'dark sea green': [143, 188, 143],
                    'medium spring green': [0, 250, 154],
                    'spring green': [0, 255, 127],
                    'sea green': [46, 139, 87],
                    'medium agua marine': [102, 205, 170],
                    'medium sea green': [60, 179, 113],
                    #aquas
                    'light sea green': [32, 178, 170],
                    'dark slate gray': [47, 79, 79],
                    'teal': [0, 128, 128],
                    'dark cyan': [0, 139, 139],
                    'aqua': [0, 255, 255],
                    'dark turquoise': [0, 206, 209],
                    'turquoise': [64, 224, 208],
                    'medium turquoise': [72, 209, 204],
                    'pale turquoise': [175, 238, 238],
                    'aqua marine': [127, 255, 212],
                    'powder blue': [176, 224, 230],
                    'cadet blue': [95, 158, 160],
                    #blues
                    'steel blue': [70, 130, 180],
                    'corn flower blue': [100, 149, 237],
                    'deep sky blue': [0, 191, 255],
                    'dodger blue': [30, 144, 255],
                    'light blue': [173, 216, 230],
                    'sky blue': [135, 206, 235],
                    'light sky blue': [135, 206, 250],
                    'midnight blue': [25, 25, 112],
                    'navy': [0, 0, 128],
                    'dark blue': [0, 0, 139],
                    'medium blue': [25, 25, 112],
                    'blue': [0, 0, 255],
                    'royal blue': [65, 105, 225],
                    #purples
                    'blue violet': [138, 43, 226],
                    'indigo': [75, 0, 130],
                    'dark slate blue': [72, 61, 139],
                    'slate blue': [106, 90, 205],
                    'medium slate blue': [123, 104, 238],
                    'medium purple': [147, 112, 219],
                    'dark magenta': [139, 0, 139],
                    'dark violet': [148, 0, 211],
                    'dark orchid': [153, 50, 204],
                    'medium orchid': [186, 85, 211],
                    'purple': [128, 0, 128],
                    'lavendar': [230, 230, 250],
                    #pinks
                    'thistle': [216, 191, 216],
                    'plum': [221, 160, 221],
                    'violet': [238, 130, 238],
                    'magenta': [255, 0, 255],
                    'orchid': [218, 112, 214],
                    'medium violet red': [199, 21, 133],
                    'pale violet red': [219, 112, 147],
                    'deep pink': [255, 20, 147],
                    'hot pink': [255, 105, 180],
                    'light pink': [255, 192, 203],
                    #egg, beige
                    'antique white': [250, 235, 215],
                    'beige': [245, 245, 220],
                    'bisque': [255, 228, 196],
                    'blanched almond': [255, 235, 205],
                    'wheat': [245, 222, 179],
                    'peach': [255, 218, 185],
                    #gray
                    'black': [0, 0, 0]
                    }

                colorGroup = {
                    #reds
                    'maroon': 'red',
                    'dark red': 'red',
                    'firebrick': 'red',
                    'crimson': 'red',
                    'red': 'red',
                    'tomato': 'red',
                    'indian red': 'red',
                    'light coral': 'red',
                    #oranges
                    'coral': 'orange',
                    'dark salmon': 'orange',
                    'salmon': 'orange',
                    'light salmon': 'orange',
                    'orange red': 'orange',
                    'dark orange': 'orange',
                    'orange': 'orange',
                    #yellows
                    'gold': 'yellow',
                    'golden rod': 'yellow',
                    'yellow': 'yellow',
                    'corn silk': 'yellow',
                    'lemon chiffon': 'yellow',
                    'light golden rod yellow': 'yellow',
                    'light yellow': 'yellow',
                    #browns
                    'brown': 'brown',
                    'dark golden rod': 'brown',
                    'pale golden rod': 'brown',
                    'dark khaki': 'brown',
                    'khaki': 'brown',
                    'saddle brown': 'brown',
                    'sienna': 'brown',
                    'chocolate': 'brown',
                    'sandy brown': 'brown',
                    'burly wood': 'brown',
                    'tan': 'brown',
                    'rosy brown': 'brown',
                    #greens
                    'olive': 'green',
                    'yellow green': 'green',
                    'dark olive green': 'green',
                    'olive drab': 'green',
                    'lawn green': 'green',
                    'chart reuse': 'green',
                    'green yellow': 'green',
                    'dark green': 'green',
                    'green': 'green',
                    'forest green': 'green',
                    'lime': 'green',
                    'lime green': 'green',
                    'light green': 'green',
                    'pale green': 'green',
                    'dark sea green': 'green',
                    'medium spring green': 'green',
                    'spring green': 'green',
                    'sea green': 'green',
                    'medium agua marine': 'green',
                    'medium sea green': 'green',
                    #aquas
                    'light sea green': 'aqua',
                    'dark slate gray': 'aqua',
                    'teal': 'aqua',
                    'dark cyan': 'aqua',
                    'aqua': 'aqua',
                    'dark turquoise': 'aqua',
                    'turquoise': 'aqua',
                    'medium turquoise': 'aqua',
                    'pale turquoise': 'aqua',
                    'aqua marine': 'aqua',
                    'powder blue': 'aqua',
                    'cadet blue': 'aqua',
                    #blues
                    'steel blue': 'blue',
                    'corn flower blue': 'blue',
                    'deep sky blue': 'blue',
                    'dodger blue': 'blue',
                    'light blue': 'blue',
                    'sky blue': 'blue',
                    'light sky blue': 'blue',
                    'midnight blue': 'blue',
                    'navy': 'blue',
                    'dark blue': 'blue',
                    'medium blue': 'blue',
                    'blue': 'blue',
                    'royal blue': 'blue',
                    #purples
                    'blue violet': 'purple',
                    'indigo': 'purple',
                    'dark slate blue': 'purple',
                    'slate blue': 'purple',
                    'medium slate blue': 'purple',
                    'medium purple': 'purple',
                    'dark magenta': 'purple',
                    'dark violet': 'purple',
                    'dark orchid': 'purple',
                    'medium orchid': 'purple',
                    'purple': 'purple',
                    'lavendar': 'purple',
                    #pinks
                    'thistle': 'pink',
                    'plum': 'pink',
                    'violet': 'pink',
                    'magenta': 'pink',
                    'orchid': 'pink',
                    'medium violet red': 'pink',
                    'pale violet red': 'pink',
                    'deep pink': 'pink',
                    'hot pink': 'pink',
                    'light pink': 'pink',
                    #egg, beige
                    'antique white': 'beige',
                    'beige': 'beige',
                    'bisque': 'beige',
                    'blanched almond': 'beige',
                    'wheat': 'beige',
                    'peach': 'beige',
                    #gray
                    'slate gray': 'gray',
                    'light slate gray': 'gray',
                    'light steel blue': 'gray',
                    'dim gray': 'gray',
                    'gray': 'gray',
                    'dark gray': 'gray',
                    'silver': 'gray',
                    'light gray': 'gray',
                    'gainsboro': 'gray',
                    'gray': 'gray',
                    # 'white': 'white',
                    'black': 'black'
                    }
                photoCap = 15
                if (numPhotos <= 15):
                    photoCap = numPhotos
                while (i < photoCap):
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

                    ########Color Analysis###########
                    NUM_CLUSTERS = 5

                    # print 'reading image'
                    fdX = urllib.urlopen(photoArray[i]['source'])
                    imX = Image.open(StringIO(fdX.read()))
                    # im = Image.open('image.jpg')
                    imX = imX.resize((150, 150))      # optional, to reduce time
                    arX = scipy.misc.fromimage(imX)
                    shape = arX.shape
                    print shape
                    arX = arX.reshape(scipy.product(shape[:2]), shape[2])

                    # print 'finding clusters'
                    codesX, distX = scipy.cluster.vq.kmeans(arX, NUM_CLUSTERS)
                    # print 'cluster centres:\n', codes

                    vecsX, distX = scipy.cluster.vq.vq(arX, codesX)         # assign codes
                    countsX, binsX = scipy.histogram(vecsX, len(codesX))    # count occurrences

                    index_maxX = scipy.argmax(countsX)                    # find most frequent
                    peakX = codesX[index_maxX]
                    colour = ''.join(chr(c) for c in peakX).encode('hex')
                    finColour = colour.decode('hex')
                    rX = str(peakX[0])
                    gX = str(peakX[1])
                    bX = str(peakX[2])

                    ##### most frequent r, g, b of the photo
                    print 'r %s g %s b %s' % (peakX[0], peakX[1], peakX[2])


                    ##### find closest corresponding color, return the color and color range

                    def dist(r, g, b, x, y, z):
                        return ((r-x)**2 + (g-y)**2 + (b-z)**2)
                   
                    mindist = 10000000000
                    answer = 'answer'

                    if (abs(peakX[0] - peakX[1]) < 15 and abs(peakX[0] - peakX[2]) < 15 and abs(peakX[1] - peakX[2]) < 15):
                        answer = 'gray'
                    else:
                        for key, value in rgbColor.iteritems():
                            x = dist(peakX[0], peakX[1], peakX[2], value[0], value[1], value[2])
                            if (x < mindist):
                                mindist = x
                                answer = key
                                xred = value [0]
                                xgreen = value[1]
                                xblue = value[2]

                    print 'closest color is %s' % (answer)

                    # print 'rgb for closest color is %d, %d, %d' % (xred, xgreen, xblue)

                    yred = peakX[0]/255.00
                    ygreen = peakX[1]/255.00
                    yblue = peakX[2]/255.00

                    Cmax = max(yred, ygreen, yblue)
                    Cmin = min(yred, ygreen, yblue)

                    #lightness calculation
                    lightness = round((Cmax+Cmin)/2, 2)
                    #saturation calculation
                    if (lightness != 0 and lightness < 1.0):
                        saturation = round(((Cmax-Cmin) / (1-abs(2*lightness-1))),2) #round((Cmax-Cmin) / (1-abs(2*lightness-1))),2)
                    else:
                        saturation = 0

                    print 'lightness %s, saturation %s' % (round(lightness, 2), round(saturation, 2))

                    prom_color = 'hi'
                    for key, value in colorGroup.iteritems():
                        if key == answer:
                            prom_color = value
                            print 'color group %s' % (value)

                    ######################

                    p = Photo(pid=photoArray[i]['id'], photo_url=photoArray[i]['source'], num_likes=numLikes,\
                            num_comments=numComments, created_time=photoArray[i]['created_time'], user=u, red=rX, green=gX, blue=bX,
                            true_color=answer, prom_color=prom_color, sat=saturation, light=lightness) 
                    db.session.add(p)
                    i = i+1
                break #we assume that only one Profile Pictures album exists!

        db.session.commit()

    return redirect(url_for('complete'))

@app.route('/complete')
def complete():
    return render_template('thankyou.html')

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