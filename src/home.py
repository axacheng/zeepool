# -*- coding: utf-8 -*-
'''
Created on Sep 4, 2010

@author: axa
'''

import auth_constants
import base64
import db_entity
import facebookoauth as foauth
import json_encoder
import logging
import os

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app


def basicAuth(func):
    def callf(webappRequest, *args, **kwargs):
        authHeader = webappRequest.request.headers.get('Authorization')
    
        if authHeader == None:
            webappRequest.response.set_status(401, message="Authorization Required")
            webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'
        else:
            auth_parts = authHeader.split(' ')
            user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
            user_arg = user_pass_parts[0]
            pass_arg = user_pass_parts[1]
  
            if user_arg != "axa" or pass_arg != "qwer1234":
                webappRequest.response.set_status(401, message="Authorization Required")
                webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'
    
                webappRequest.response.out.write("Oopsssssss 你需要漢程醬醬要授權")
            else:
                return func(webappRequest, *args, **kwargs)
  
    return callf


class AuthHandler(webapp.RequestHandler):
    """ Compile OpenID/Federated User and Oauth user authentication links.
    
    Read in auth_constants.py, then process OpenIdProviders and OauthProviders
    their federated_identity or direct Oauth link and generate login URLs.
    Here, I use dict update() to merge those two providers links.
    
    Return:  dict: JSON object.
        The return will be executed by WSGI /auth_handler when index.html
        login.js being executed.
    """
    def get(self):
        for openid_provider, openid_data in auth_constants.OpenIdProviders.items():
            op_url = openid_provider.lower() #e.g. google.com
            #openid_data['url'] = users.create_login_url(federated_identity=op_url)
            #Uncomment for local testing server.
            openid_data['url'] = users.create_login_url(
               dest_url="/", federated_identity=op_url)

        oauth_provider_links = auth_constants.OauthProviders
        oauth_provider_links.update(auth_constants.OpenIdProviders)
        login_links = oauth_provider_links #Merge openid and oauth together then rename it.
        logging.info('URLs %s' % login_links)
        self.response.out.write(simplejson.dumps(login_links)) # Convert links to JSON format       
        

def UserLoginHandler(self):
    """ This method can be called by MainPage get() method.
    
    Two kinds of account support: OpenID and Oauth.
    * OpenID
      1. GAE has built-in federated support. Yahoo and Google use it.
      
    * Oauth
      1. Facebook user: 
      2. Sina weibo user: Similar as facebook API but I use standard oauth 1.0
                     protocol to get access_token then use it token with weibo
                     weibopy.api API to get username. I use 'sina_username'
                     cookie to control user login/logout status.
                     
    Return: dict: logged in username:logout URL link
    """
    # Check OpenID/Federated user logged in or not.
    openid_username = users.get_current_user()
     
    # Check Facebook user logged in or not.
    if not hasattr(self, "_current_user"):
        self._current_user = None
        user_id = foauth.parse_cookie(self.request.cookies.get("fb_user"))
        #logging.info('I am Facebook User ID: %s' % user_id)

        if user_id:
            self._current_user = foauth.FacebookUser.get_by_key_name(user_id)
    facebook_user =  self._current_user #Returns FacebookUser db entity

    if openid_username:
        logging.info('OpenID USER NAME: %s' % openid_username)
        logout_link = users.create_logout_url(self.request.path)
        return {openid_username.nickname():logout_link}

    elif facebook_user:
        logging.info("I am Facebook User %s" % facebook_user)
        logout_link = '/oauth/facebook_logout'
        return {facebook_user.name:logout_link}
    
    else:
        logging.info('We cant find username, and would generate  USER NAME')
        return {}
        

class MainPage(webapp.RequestHandler):
    """ Represent the MainPage - index.html
    
    First of all, we check OpenID or Oauth user login status by fetching their
    'username' which handled by UserLoginHandler() class.
    When 'username' is False which means user hasn't been login yet, in this
    case we would insert multiple <span> html tags as login_url links and
    account provider's logo (e.g. google, yahoo or facebook icon) to
    index.html <div class=login_auth>. You can check login.js to get more detail
    information.
    
    MainPage-->UserLoginHandler (no username) --> 
                 1. Activate <div class='login_auth'>
                 2. login.js calls /auth_handler (aka: AuthHandler()), and
                    return(aka: login_link) would be appended by jQuery to 
                    generate <span> tag for login links.
                 3. AuthHandler() generates login_urls and image link for
                    OauthProviders user, and for OpenIdProviders user we use
                    users.create_login_url method to generate url_link.
    MainPage-->UserLoginHandler (has username) -->
                 1. Activate <div id="add_main"> and skip <div class='login_auth>
                 2. Construct logout_link, url_text, login_status, query
                 3. Render to index.html
                 
    * For OpendID user, their login_status can be verified by user GAE build-in
    function - get_current_user().It's simple!
    * For Oauth user such as Facebook, we can get their /me.name (provided from
    FB.api return) by using GAE WSGI self.request.get() method on index.html.
    
    
    Return: WSGIApplication with html object
    """
    @basicAuth
    def get(self):
        username = "".join(UserLoginHandler(self).keys())
        logout_link = "".join(UserLoginHandler(self).values())
        
        if username:
            url_link = logout_link
            url_text = '登出'
            login_status = True
            query = db_entity.Words.all().filter('Creator =', username)
        else:
            logging.info('No login username be found.')
            url_link = users.create_login_url(self.request.path)
            url_text = '先登入才能增加新字'
            login_status = None
            query = None
            
        # Session for count amount of Words. Even username is None, we're going
        # to render our amount of Words to everyone.
        all_words_count = db_entity.Words.all()
        total_words = all_words_count.count()       
                                      
        # Compile all the 'key' to template_dict and pass them to index.html
        # This url_link could be logout_link or login_link depends on whether
        # username exist or not. If it's exist then url_link is logout_link,
        # vice versa. 
        template_dict = {'url_link':url_link, 'url_text':url_text,
                         'login_status':login_status,
                         'total_words':total_words,
                         'query':query,}
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_dict))
    

class Search(webapp.RequestHandler):
    @basicAuth
    def get(self):
        """ Search result handler.
        
        Use request.get('term') to fetch <input id="search_input" name="term" > 
        from index.html. The reason I use 'term' instead of 'q' that's because
        jqueryUI autocomplete use 'term' this string to GET.
        
        Return: dict: JSON object with query result and total found words.
        
        """
        search_word = self.request.get('term')
        query = db_entity.Words.gql('WHERE Word >= :word_begin and Word <= :word_end',
                                  word_begin=unicode(search_word),
                                  word_end=unicode(search_word) + u'\ufffd')
        result = query.fetch(50, 0)

        if query.count() == 0:
            # json_result is pure string type.
            json_result = json_encoder.GqlEncoder().encode(result)            
            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json_result)
        else:
            total_words = '"TotalWords":' + str(query.count())
            # json_result is pure string type.
            json_result = json_encoder.GqlEncoder().encode(result)
            
            # Rid of '[' and ']' at very beginning and end of json_result.
            # Also remove '}' at the end then add dict of total_words
            # Before out.write to client add '[' and ']' surround to be JSON format
            result = json_result.strip('[]').rstrip('}') + ',' + total_words + "}"
            self.response.headers['Content-Type'] = "application/json"         
            self.response.out.write('[' + result + ']')

  
class Add(webapp.RequestHandler):
    @login_required
    def get(self):
        pass
    
    def post(self):
        username = "".join(UserLoginHandler(self).keys())

        if username:
            creator = username
            word = self.request.get("word")
            define = self.request.get("define")
            example = self.request.get("example")
            tags = self.request.get("tag").split(',')
            new_tags = map(lambda x:x.strip(), tags)
            try:
                create_entity = db_entity.Words(Creator=creator,
                                                Word=word,
                                                Define=define,
                                                Example=example,
                                                Tag=new_tags)
                create_entity.put()
                response = {'status':'success', 'message':'存檔成功了'}
                # using following way can convert chinese unicode to utf8
                #http://deron.meranda.us/python/comparing_json_modules/unicode
                json_ustr = simplejson.dumps(response, ensure_ascii=False)
                self.response.out.write(json_ustr)
            except ValueError:
                response = {'status':'error', 'message':'資料庫壞了...維修中'}
                # using following way can convert chinese unicode to utf8
                json_ustr = simplejson.dumps(response, ensure_ascii=False)
                self.response.out.write(json_ustr)
        else:
            self.redirect(users.create_login_url(self.request.uri))


class Edit(webapp.RequestHandler):
    @basicAuth
    def get(self, username):
        pass

    def post(self):
        submitted_div = self.request.get('id')
        key = submitted_div[1:]
        type = submitted_div[0] # Have 3 types: d,e,t
        query = db_entity.Words.get(key)
        if type == 'd':
            query.Define = self.request.get('value')
            self.response.out.write(query.Define)
        if type == 'e':        
            query.Example = self.request.get('value')
            self.response.out.write(query.Example)
        if type == 't':
            query.Tag = self.request.get('value')
            self.response.out.write(query.Tag)
        #import sys
        #print >> sys.stderr, key, query.Define, query.Example
        query.put()


class SingleWord(webapp.RequestHandler):
    def get(self, key):
        query = db_entity.Words.get(key)
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(query)
        #result = query.Word
        #self.response.out.write(result)
        
        
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/add', Add),
                                      ('/edit', Edit),
                                      ('/oauth/facebook_login', foauth.LoginHandler),
                                      ('/oauth/facebook_logout', foauth.LogoutHandler),
                                      ('/auth_handler', AuthHandler),
                                      ('/search', Search),
                                      ('/word/(.*)', SingleWord)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()