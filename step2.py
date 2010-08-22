from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
import atom.url
import gdata.service
import gdata.alt.appengine
import settings


class Fetcher(webapp.RequestHandler):

    def get(self):
        # Write our pages title
        self.response.out.write("""<html><head><title>
            Google Data Feed Fetcher: read Google Data API Atom feeds</title>""")
        self.response.out.write('</head><body>')
        # Allow the user to sign in or sign out
        next_url = atom.url.Url('http', settings.HOST_NAME, path='/step2')
        if users.get_current_user():
            self.response.out.write('<a href="%s">Sign Out</a><br>' % (
                users.create_logout_url(str(next_url))))
        else:
            self.response.out.write('<a href="%s">Sign In</a><br>' % (
                users.create_login_url(str(next_url))))

        # Initialize a client to talk to Google Data API services.
        client = gdata.service.GDataService()
        gdata.alt.appengine.run_on_appengine(client)
	feed_url = self.request.get('feed_url')


        session_token = None
        # Find the AuthSub token and upgrade it to a session token.
        auth_token = gdata.auth.extract_auth_sub_token_from_url(self.request.uri)
        if auth_token:
            # Upgrade the single-use AuthSub token to a multi-use session token.
	    session_token = client.upgrade_to_session_token(auth_token)
        if session_token and users.get_current_user():
            # If there is a current user, store the token in the datastore and
            # associate it with the current user. Since we told the client to
            # run_on_appengine, the add_token call will automatically store the
            # session token if there is a current_user.
            client.token_store.add_token(session_token)
        elif session_token:
            # Since there is no current user, we will put the session token
            # in a property of the client. We will not store the token in the
            # datastore, since we wouldn't know which user it belongs to.
            # Since a new client object is created with each get call, we don't
            # need to worry about the anonymous token being used by other users.
            client.current_token = session_token

        self.response.out.write('<div id="main"></div>')
	self.fetch_feed(client, feed_url)
        self.response.out.write(
            '<div id="sidebar"><div id="scopes"><h4>Request a token</h4><ul>')
        self.response.out.write('<li><a href="%s">Google Documents</a></li>' % (
            client.GenerateAuthSubURL(
                next_url,
                ('http://docs.google.com/feeds/',), secure=False, session=True)))
        self.response.out.write('</ul></div><br/><div id="tokens">')

    def fetch_feed(self, client, feed_url):
        # Attempt to fetch the feed.
        if not feed_url:
            self.response.out.write(
                'No feed_url was specified for the app to fetch.<br/>')
            example_url = atom.url.Url('http', settings.HOST_NAME, path='/step3',
                params={'feed_url':
                    'http://docs.google.com/feeds/documents/private/full'}
                ).to_string()
            self.response.out.write('Here\'s an example query which will show the'
                ' XML for the feed listing your Google Documents <a '
                'href="%s">%s</a>' % (example_url, example_url))
            return
        try:
            response = client.Get(feed_url, converter=str)
            self.response.out.write(cgi.escape(response))
        except gdata.service.RequestError, request_error:
            # If fetching fails, then tell the user that they need to login to
            # authorize this app by logging in at the following URL.
            if request_error[0]['status'] == 401:
                # Get the URL of the current page so that our AuthSub request will
                # send the user back to here.
                next = atom.url.Url('http', settings.HOST_NAME, path='/step3',
                    params={'feed_url': feed_url})
                # If there is a current user, we can request a session token, otherwise
                # we should ask for a single use token.
                auth_sub_url = client.GenerateAuthSubURL(next, feed_url,
                    secure=False, session=True)
                self.response.out.write('<a href="%s">' % (auth_sub_url))
                self.response.out.write(
                    'Click here to authorize this application to view the feed</a>')
            else:
                self.response.out.write(
                    'Something went wrong, here is the error object: %s ' % (
                        str(request_error[0])))

def main():
    application = webapp.WSGIApplication([('/.*', Fetcher),], debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
