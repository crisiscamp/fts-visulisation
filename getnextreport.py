import urllib2
import httplib

# Read file from url
# Code based on http://diveintopython.org/http_web_services/user_agent.html
# and http://diveintopython.org/http_web_services/etags.html
# on 22/08/2010
def getNewReport(etag=None)
    request = urllib2.Request("http://fts.unocha.org/reports/daily/OCHA_R32sum_A905.XLS")
    opener = urlib2.build_opener()
    request.add_header('User-Agent', 'FSTDynamicCharting/1.0')
    request.add_header('If-None-Match', etag)
    filedata = opener.open(request).read()
    return filedata

def updateGoogleDocs()
