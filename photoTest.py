import struct
from PIL import Image
import scipy
import scipy.misc
import scipy.cluster
from StringIO import StringIO
import urllib2 as urllib

NUM_CLUSTERS = 5

# print 'reading image'
fdX = urllib.urlopen("http://graph.facebook.com/1578957057/picture?type=square")
imX = Image.open(StringIO(fdX.read()))
# im = Image.open('image.jpg')
imX = imX.resize((150, 150))      # optional, to reduce time
arX = scipy.misc.fromimage(imX)
shape = arX.shape
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
red = peakX[0]
green = peakX[1]
blue = peakX[2]
# print '%s' % (colour)
# print 'most frequent is %s (#%s)' % (peakX, finColour)
# print 'r %s g %s b %s' % (peakX[0], peakX[1], peakX[2])
print peakX
print peakX[2]
print type(peakX[2])
print type(1)
print type(str(peakX[2]))

dict = {'key':val}
def dist(r, g, b, x, y, z):
	return ((r-x)**2 + (g-y)**2 + (b-z)**2)
for key, value in d.iteritems():