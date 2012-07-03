# -*- coding: utf-8 -*-
'''
Created on Sep 4, 2010

@author: Axa Cheng
'''
import auth_constants
import base64
import db_entity
import datetime
import facebookoauth as foauth
import logging
import operator
import os
import random
import weibo_oauth_v2
import webapp2

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
    
    
MAX_SEARCH_RESULT_PER_PAGE = 3
    
class Add(webapp2.RequestHandler):
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
                logging.info('%s added new word: %s', username, word)
                
                # SearchPagingCounter would increment by one after new word added.
                SearchCounter(action='add_count')
                
                
                # using following way can convert chinese unicode to utf8
                #http://deron.meranda.us/python/comparing_json_modules/unicode
                json_ustr = simplejson.dumps(response, ensure_ascii=False)
                self.response.out.write(json_ustr)
            except ValueError:
                response = {'status':'error', 'message':'資料庫壞了...維修中'}
                logging.info(response)
                # using following way can convert chinese unicode to utf8
                json_ustr = simplejson.dumps(response, ensure_ascii=False)
                self.response.out.write(json_ustr)
        else:
            self.redirect(users.create_login_url(self.request.uri))


class AuthHandler(webapp2.RequestHandler):
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


class Edit(webapp2.RequestHandler):
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


class MainPage(webapp2.RequestHandler):
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
    
    
    Return: WSGIApplication with html object with dict type
           {template_dict}
               'url_link': login or logout URL link.
               'url_text': Description for url_link.
               'login_status': If UserLoginHandler return True, then it'd be 
                               True in login_status. Otherwise, None.
               'user_editable_word': All the words created by logged in user.
                                     Return here would be reused for rendering
                                     /edit page. (aka: /#myAnchor)
    """
    @basicAuth
    def get(self):
        username = "".join(UserLoginHandler(self).keys())
        logout_link = "".join(UserLoginHandler(self).values())
        #username = "692733281:Axa Cheng@facebook"
        
        if username:
            url_link = logout_link
            url_text = '登出'
            login_status = True
            user_editable_word = db_entity.Words.all().filter('Creator =', username)
        else:
            logging.info('No login username be found.')
            url_link = users.create_login_url(self.request.path)
            url_text = '先登入才能增加新字'
            login_status = None
            user_editable_word = None
            
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
                         'user_editable_word':user_editable_word,}
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_dict))

def PollCounter(pollword_choose, pollword_key, username, display_for_search=True):
  if display_for_search:  # Only display total count result for Search result.
    total_like = 0
    total_dislike = 0
    counters_like = db_entity.CounterLikeWord.all().filter('name =', pollword_key)
    counters_dislike = db_entity.CounterDislikeWord.all().filter('name =', pollword_key)

    for counter_like in counters_like:
      total_like += counter_like.value

    for counter_dislike in counters_dislike:
      total_dislike += counter_dislike.value

    response = {'total_like_count': total_like,
                'total_dislike_count': total_dislike}
    logging.info(response)

    return response

  else:
    """ Add users like or dislike on Word.
    It'd be called by 'PollWord' handler that requested by /autocom.js
    Poll system. find '$(".pollword").live' on autocom.js
    We probably wont to fetch db again for lighting db loading.
    And, we would use jQuery to make 'fake' increment by 1 result to user.
    That's why after counter.put() , we won't have return/json return to caller.
    """
    counter = db_entity.CounterLikeWord.all().filter('name =', pollword_key).filter('Creator =', username).fetch(4)

    if not counter:
      logging.info('%s is going to vote on %s', username, pollword_key)
      shard_name = '%s_%s' % (pollword_key, str(random.randint(1, 4)))

      if pollword_choose == 'like':
        counter = db_entity.CounterLikeWord.get_by_key_name(shard_name)
        if counter is None:
          counter = db_entity.CounterLikeWord(key_name=shard_name,
                                              name=pollword_key)
        counter.value += 1
        counter.Creator = username
        counter.put()
      else:
        counter = db_entity.CounterDislikeWord.get_by_key_name(shard_name)

        if counter is None:
          counter = db_entity.CounterDislikeWord(key_name=shard_name,
                                                 name=pollword_key)
        counter.value += 1
        counter.Creator = username
        counter.put()

    else:
      logging.info('%s, You can not vote to same word:%s twice.',
                   username, pollword_key)
 

class PollWord(webapp2.RequestHandler):
  """ pollword_choose, like or dislike  (TODO) """
  def get(self, pollword_choose, pollword_key):
    username = "".join(UserLoginHandler(self).keys())
    PollCounter(pollword_choose, pollword_key, username, display_for_search=False)
    

class Search(webapp2.RequestHandler):
    @basicAuth
    def get(self, page):
        """ Search result handler.
        
        Use request.get('term') to fetch <input id="search_input" name="term" > 
        from index.html. The reason I use 'term' instead of 'q' that's because
        jqueryUI autocomplete use 'term' this string to GET.
        
        Return: dict: JSON object with query result and total found words.
                      if query.fetch() gets zero result from datastore, it'll
                      return [] to json.dump.
                      if query.fetch() gets result more than once from datastore
                      , then we build dict(fetched_word) and [all_word] structure.
                      
                      For the Poll word count, we use PollCounter() method to
                      fetch the 'like' and 'dislike' counting result from
                      CounterLikeWord and CounterDislikeWord datastore, and then
                      we unzip value by their key 'total_like_count' and 
                      'total_dislike_count'. Finally, fetched_word would store 
                      all the data as multiple dicts, then we use all_word to
                      merge multiple dicts into a list for json.
                      e.g.: all_words = [{'Word':'a'}, {'Word':'b'}]
                      
                      The main reason we use [all_word] that's because the dicts
                      uses same key 'Word' as dict's key so we should use list
                      to merge multiple dicts.
                
        """
        if len(page):
            page = int(page)
        else:
            page = 1
                   
        all_word = []
        search_word = self.request.get('term')
        query = db_entity.Words.all()
        
        query.filter("Display", True)
        query.filter("Word >=", unicode(search_word))
        query.filter("Word <=", unicode(search_word) + u'\ufffd')
        result = query.fetch(500, 0)
        total_searched_words = query.count()  # (TODO) get rid of count() it's dangerous!
        
        if result:  
          for p in result:
            word_count = PollCounter(None, str(p.key()), None, display_for_search=True)
            logging.info('This is word count %s', word_count)
            fetched_word = {}
            fetched_word['key'] = str(p.key())
            fetched_word['Word'] = p.Word
            fetched_word['Creator'] = p.Creator.split(':')[1]
            fetched_word['Tag'] = p.Tag
            fetched_word['Example'] = p.Example
            fetched_word['Define'] = p.Define
            fetched_word['Created'] = p.Created.strftime('%Y-%m-%d')
            fetched_word['Like'] = word_count['total_like_count']
            fetched_word['Dislike'] = word_count['total_dislike_count']
            all_word.append(fetched_word)
            
          sorted_by_like_all_word = sorted(all_word, reverse=True,
                                           key=operator.itemgetter('Like'))
          all_word = PagingSearchResult(page, sorted_by_like_all_word)
          
          
          logging.info('Searched word is: %s', p.Word )  
          logging.info('server return: %s', all_word)
          total_words = {'total_words':total_searched_words}
          path = os.path.join(os.path.dirname(__file__), 'search_result.html')
          self.response.out.write(template.render(path, {
                                                         'search_results':all_word,
                                                         'total_words':total_words}))
          
        else:
          logging.info('zero result')
          json_result = simplejson.dumps(result)
          self.response.headers.add_header("Content-Type",
                                           "application/json charset='utf-8'")
          self.response.out.write(json_result)


def PagingSearchResult(page, sorted_by_like_all_word):
    """ Build a python list slice to indent 
    
    """
    first_word = MAX_SEARCH_RESULT_PER_PAGE * (page - 1)
    last_word  = MAX_SEARCH_RESULT_PER_PAGE * page
    return sorted_by_like_all_word[first_word:last_word]
    


def SearchCounter(action):
    if action == 'add_count':
        shard_name = 'search_paging_shard_%s' % str(random.randint(1, 10))
        counter = db_entity.SearchPagingCounter.get_by_key_name(shard_name)
        if counter is None:
            counter = db_entity.SearchPagingCounter(key_name=shard_name, name='search_paging')
        counter.value += 1
        counter.put() 
"""
    elif action == 'get_count':
        total = 0
        counters = db_entity.SearchPagingCounter.all().filter('name', 'search_paging')
        
        if counters is None:
            total_page = 1
        else:
            for counter in counters:
                total += counter.value
            total_page = total / MAX_SEARCH_RESULT_PER_PAGE  # (TODO) need to use constents instead.
            if total % MAX_SEARCH_RESULT_PER_PAGE > 0:
                total_page = total_page + 1
            return total_page
"""

def UserLoginHandler(self):
    """ This method offers username and logout_link to MainPage().
    
    MainPage() would see if current uesr is logged in, or needed to log in.
    If current user shows 'no logged in', then we would provide login links to
    them which handled by AuthHandler().
    If current user is logged in, then here we provide logout link, and it'd
    being a result to template_dict['url_link']
    
    Two kind of account authorizations support: OpenID and Oauth2.0.
    * OpenID
      1. GAE has built-in federated support. Yahoo and Google use it.
      
    * Oauth2.0
      1. Facebook user: We use unofficial facebook python API - facebookoauth.py
         and changed it a bit for customization. 
         http://github.com/pythonforfacebook/facebook-sdk (version 0.3.0)
         
         This API sets cookie(fb_user) to browser, and we use
         foauth.parse_cookie function to get it back from user's browser
         resource to identify your profile info (e.g. access_token or login 
         status)
      
      2. Sina weibo user: Similar as Facebook python API.
         When your click Weibo login icon on our page, we will deliver your to
         weibo authentication page to get access_token by OAuth2.0.
         Once authentication flow successful then we set "weibo_user" cookie on
         user's browser. When main page loaded, we would check weibo_user cookie
         by parse_cookie method which would decode cookie format and pull Weibo
         User's ID out. More detail check:
             weibo_oauth_v2.py line 112: 'weistr(weibo_user_profile.id)' 
             weibo_oauth_v2.py line 142:  set_cookie(self.response, 
                                                     "weibo_user",
                                                     str(weibo_id),
        About the decode, you can check weibo_oauth_v2.py line 173
              base64.b64decode(parts[0]).strip()
        
        Once we got Weibo user's ID, then we use it as datastore key_name to
        fetch its value(aka: Weibo username) from screen_name column.
        Finally, we use screen_name to determine user login or not.
                   
    Return: dict: {logged in username:logout URL link}
    """
    # Check OpenID/Federated user logged in or not.
    openid_username = users.get_current_user()
     
    # Check Facebook user logged in or not.
    if not hasattr(self, "_current_user"):
        self._current_user = None
        user_id = foauth.parse_cookie(self.request.cookies.get("fb_user"))

        if user_id:
            self._current_user = foauth.FacebookUser.get_by_key_name(user_id)
    facebook_user =  self._current_user #Returns FacebookUser db entity

    # Check WeiBo user logged in or not.
    weibo_cookie = weibo_oauth_v2.parse_cookie(self.request.cookies.get("weibo_user"))
    if weibo_cookie:
      weibo_user_id = weibo_cookie
      weibo_user_ancestor = weibo_oauth_v2.WeiboUser.get_by_key_name(weibo_user_id)
      query = db.Query(weibo_user_ancestor)
      for name in query.fetch(1):
        weibo_screen_name = name.screen_name
       
      weibo_username = weibo_user_id + ':' + weibo_screen_name + '@weibo'
      
    else:
      weibo_username = None
      
      
    if openid_username:
        #openid_user_id = ':' + openid_username.user_id()  #1111
        openid_username = openid_username.user_id() + ':' + openid_username.email()
        #openid_username = openid_username.email().replace('@', openid_user_id)
        logging.info('%s logged in.' % openid_username)
        logout_link = users.create_logout_url(self.request.path)
        return {openid_username:logout_link}

    elif facebook_user:
        facebook_user = facebook_user.id + ':' + facebook_user.name + '@facebook'
        logging.info("%s logged in." % facebook_user)
        logout_link = '/oauth/facebook_logout'
        return {facebook_user:logout_link}

    elif weibo_username:
        logging.info("%s logged in." % weibo_username)
        url_link = '/oauth/weibo_logout'
        return {weibo_username:url_link}

    else:
        logging.info('We cant find username, redirect to login page.')
        return {}

        
class GenerateFakeData(webapp2.RequestHandler):
    def get(self):
        fake_word = {'milf1': ['define1', 'example1', 'tag1'],
                     'milf2': ['define2', 'example2', 'tag2'],
                     'milf3': ['define3', 'example3', 'tag3'],
                     'milf4': ['define4', 'example4', 'tag4'],
                     'milf5': ['define5', 'example5', 'tag5'],
                     'milf6': ['define6', 'example6', 'tag6'],
                     'milf7': ['define7', 'example7', 'tag7'],
                     'milf8': ['define8', 'example8', 'tag8'],
                     'milf9': ['define9', 'example9', 'tag9'],
                     'milf14': ['define14', 'example14', 'tag14']}                                         

        
        for i in fake_word.items():
            ccc = db_entity.Words(Creator='692733281:Axa Cheng@facebook',
                                  Word=i[0],
                                  Define=i[1][0],
                                  Example=i[1][1],)
            ccc.put()
        self.redirect('/')

                
                
app = webapp2.WSGIApplication(
                                     [('/', MainPage),
                                      ('/add', Add),
                                      ('/edit', Edit),
                                      ('/oauth/facebook_login', foauth.LoginHandler),
                                      ('/oauth/facebook_logout', foauth.LogoutHandler),
                                      ('/oauth/weibo_login', weibo_oauth_v2.LoginHandler),
                                      ('/oauth/weibo_logout', weibo_oauth_v2.LogoutHandler),
                                      ('/auth_handler', AuthHandler),
                                      ('/pollword/(.*)/(.*)', PollWord),
                                      ('/search/(\d*)', Search),
                                      ('/fake', GenerateFakeData)
                                      ],
                                     debug=True)