#!/usr/bin/python 

"""
The MIT License

Copyright (c) 2007 Leah Culver

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

This is originally from oauth code and Axa modified it.
  http://oauth.googlecode.com/svn/code/python/oauth/example/client.py
"""

import datetime
import httplib
import sys
import logging
import oauth
import random
import time

from weibopy.api import API
from weibopy.auth import OAuthHandler
from google.appengine.ext import webapp
from google.appengine.api import memcache


# fake urls for the test server (matches ones in server.py)
ACCESS_TOKEN_URL = 'http://api.t.sina.com.cn/oauth/access_token'
AUTHORIZATION_URL = 'http://api.t.sina.com.cn/oauth/authorize'
CALLBACK_URL = 'zeepooling.appspot.com'
CONSUMER_KEY = '1496964127'
CONSUMER_SECRET = 'ec756023d85cd93846a7fe52d7b6d784'
PORT = 80
REQUEST_TOKEN_URL = 'http://api.t.sina.com.cn/oauth/request_token'
RESOURCE_URL = 'zeepooling.appspot.com'
SERVER = 'api.t.sina.com.cn'

# Set cookie. Expiration is 2 days long.
expires = datetime.datetime.now() + datetime.timedelta(days=2)
expires_rfc822 = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
cookie = "; expires=%s; path=/" % expires_rfc822


class SimpleOAuthClient(oauth.OAuthClient):
    def __init__(self, server, port=httplib.HTTP_PORT, request_token_url='',
                 access_token_url='', authorization_url=''):
        self.server = server
        self.port = port
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url
        self.connection = httplib.HTTPConnection("%s:%d" % (self.server, 
                                                            self.port))

    def fetch_request_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection.request(oauth_request.http_method,
                                self.request_token_url,
                                headers=oauth_request.to_header()) 
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def fetch_access_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection.request(oauth_request.http_method,
                                self.access_token_url,
                                headers=oauth_request.to_header()) 
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def authorize_token(self, oauth_request):
        # via url
        # -> typically just some okay response
        self.connection.request(oauth_request.http_method,
                                oauth_request.to_url()) 
        response = self.connection.getresponse()
        return response.read()


class SinaOauthPhaseOne(webapp.RequestHandler):
    def get(self):
        # setup/initial
        client = SimpleOAuthClient(SERVER, PORT, REQUEST_TOKEN_URL,
                                   ACCESS_TOKEN_URL, AUTHORIZATION_URL)
        consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

        # get request token
        # print '* Obtain a request token ...'
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                            consumer,
                            callback=CALLBACK_URL,
                            http_url=client.request_token_url)
        oauth_request.sign_request(signature_method_plaintext, consumer, None)
    
        #print 'REQUEST (via headers)'
        #print 'parameters: %s' % str(oauth_request.parameters)
        cid = str(int(random.uniform(0,sys.maxint)))
        token = client.fetch_request_token(oauth_request)
        memcache.set("PK_"+cid, token.to_string())
        PHASETWO_CALLBACK_URL = 'http://zeepooling.appspot.com/oauth_authorized?id=' + cid

        #print '* Authorize the request token ...'
        oauth_request = oauth.OAuthRequest.from_token_and_callback(
                            token=token,
                            callback=PHASETWO_CALLBACK_URL,
                            http_url=client.authorization_url)
        #??? response = client.authorize_token(oauth_request)
        #??? self.redirect(response)
        # OR USING BELOW LINES instead ?
        oauth_request.sign_request(signature_method_hmac_sha1, consumer, token)
        self.redirect(oauth_request.to_url())
        
        
class SinaOauthPhaseTwo(webapp.RequestHandler):
    # get access token
    def get(self):
        verifier = self.request.get('oauth_verifier')
        logging.info('verify id = %s' % verifier)
        
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        
        # Get token - key and secret from memcache that we set on SinaOauthPhaseOne
        tokenstr = memcache.get("PK_"+self.request.get('id'))
        memcache.delete("PK_"+self.request.get('id'))
        token = oauth.OAuthToken.from_string(tokenstr)                
               
        consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        client = SimpleOAuthClient(SERVER, PORT, REQUEST_TOKEN_URL,
                                   ACCESS_TOKEN_URL, AUTHORIZATION_URL)
        
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                            consumer,
                            token=token, verifier=verifier,
                            http_url=client.access_token_url)
        oauth_request.sign_request(signature_method_hmac_sha1, consumer, token)
        
        # Finally get access_token after verifier is matched.
        access_token = client.fetch_access_token(oauth_request)
        logging.info('Sina Authorized access_token = %s' % access_token)
        
        # Set cookie into browser in case for further use.
        self.response.headers.add_header('Set-Cookie',
                                         'oauth_key=' + access_token.key + cookie)
        self.response.headers.add_header('Set-Cookie',
                                         'oauth_secret=' + access_token.secret + cookie)
        
        # Call Sina weibopy API auth.OAuthHandler() and set access_token to
        # fetch access_resource aka:user resource.
        auth_access_resource = OAuthHandler(
                                    consumer_key=CONSUMER_KEY,
                                    consumer_secret=CONSUMER_SECRET)
        auth_access_resource.set_access_token(access_token.key,
                                              access_token.secret)
        
        # API() inherits auth_access_resource return.
        api = API(auth_access_resource)
        
        # I call api.verify_credentials instead of use auth.OAuthHandler.get_username
        username = api.verify_credentials()
 
        if username:
            self.username = username.screen_name
            self.response.headers.add_header('Set-Cookie',
                                             'sina_username=' + self.username + cookie)
            logging.info('Sina username: %s' % self.username)
        else:
            logging.info('NO SINA USER %s' % self.username)

        
        self.redirect('/')


class LogoutHandler(webapp.RequestHandler):
    def get(self):
        expires_rfc822 = time.time() - 86400
        cookie = "; expires=%s; path=/" % expires_rfc822
        self.response.headers.add_header('Set-Cookie',
                                         'sina_username=' + "" + cookie)
        self.redirect("/")