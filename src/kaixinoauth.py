# -*- coding: utf-8 -*-

import logging
import os
import time

from django.utils import simplejson as json
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template


KAIXIN_APP_ID = "117623761632031"
KAIXIN_APP_SECRET = "5570aa4b96c37a86f3e9dedba0766f73"
KAIXIN_URL = "http://rest.kaixin001.com/api/rest.php"


class KaixinUser(db.Model):
    id = db.StringProperty(required=True)
    current_session_key = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)


class KaiXinCallback(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), "kx001_receiver.html")
        session_key =  self.request.cookies.get("kx_connect_session_key")

        if not session_key:
            logging.info('NO session_key: %s But we are going to set it' % session_key)
            session_key = self.request.cookies.get("kx_connect_session_key")
            self.response.out.write(template.render(path, {}))
        else:
            logging.info('YES session_key: %s' % session_key)
            
        #uid = parse_cookie(self.request.cookies.get("_uid"))
        #uid = '56083049'
        #param = {'api_key':KAIXIN_APP_ID, 'call_id':(datetime.datetime.now()).microsecond,
        #         'format':'json', 'method':'users.getInfo',
        #         'uids':uid, 'session_key':session_key, 'v': '1.0'}
        
        #sig = hashlib.md5(str(re.sub(r'\s', '', str(param).replace(':','=')).strip('{}').replace('\'','').replace(',','')+KAIXIN_APP_SECRET)).hexdigest()
        #param['sig'] = sig
        #post_param = urllib.urlencode(param)
        #response = json.load(urllib.urlopen(KAIXIN_URL, post_param))
        #print >> sys.stderr, param, post_param, response
        #urllib.urlopen(KAIXIN_URL, post_param)
        #unicode_string = unicode(response)  
        #self.response.out.write(unicode_string.encode('utf-8'))  


class LogoutHandler(webapp.RequestHandler):
    def get(self):
        expires_rfc822 = time.time() - 86400
        cookie = "; expires=%s; path=/" % expires_rfc822
        self.response.headers.add_header('Set-Cookie',
                                         'kx_connect_session_key=' + "" + cookie)
        self.redirect("/")