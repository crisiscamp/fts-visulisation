from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
import atom.url
import gdata.service
import gdata.alt.appengine
import settings


class Fetcher(webapp.RequestHandler):

    def get(self):
        next_url = atom.url.Url('http', settings.HOST_NAME, path='/step1')

        # Initialize a client to talk to Google Data API services.
        client = gdata.service.GDataService()
        gdata.alt.appengine.run_on_appengine(client)

        # Generate the AuthSub URL and write a page that includes the link
        self.response.out.write("""<html><body>
            <a href="%s">Request token for the Google Documents Scope</a>
            </body></html>""" % client.GenerateAuthSubURL(next_url,
                ('http://docs.google.com/feeds/',), secure=False, session=True))


def main():
    application = webapp.WSGIApplication([('/.*', Fetcher),], debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
