# -*- coding: utf-8 -*-

#!/usr/bin/env python
#
# Copyright 2012
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

""" This code is changed by Axa for WeiBo Oauth2.0

"""

import base64
import Cookie
import email.utils
import hashlib
import hmac
import logging
import os.path
import time
import webapp2

from weibo import APIClient
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template


WEIBO_APP_KEY='1496964127'
WEIBO_APP_SECRET='ec756023d85cd93846a7fe52d7b6d784'
        
# This CALLBACK_URL must be the same as :
# http://open.weibo.com/apps/1496964127/info/advanced
# 裡面的 "应用回调页" Otherwise, you would get 'error:redirect_uri_mismatch'
CALLBACK_URL='http://zeepooling-hrd.appspot.com/oauth/weibo_login'  
        
        
class WeiboUser(db.Model):
    access_token = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    id = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    profile_image_url = db.StringProperty(required=True)
    screen_name = db.StringProperty(required=True)
    updated = db.DateTimeProperty(auto_now=True)


class BaseHandler(webapp2.RequestHandler):
    @property
    def current_user(self):
        """Returns the logged in Weibo user, or None if unconnected."""
        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = parse_cookie(self.request.cookies.get("weibo_user"))
            if user_id:
                self._current_user = WeiboUser.get_by_key_name(user_id)
        return self._current_user
         

class LoginHandler(BaseHandler):
      """ WeiBo APIClient login testing.
      
      When user first time to get in our site, they should request 'code'
      by using url=client.get_authorize_url() to compile URL e.g.:
      https://api.weibo.com/oauth2/authorize?redirect_uri=http%3A//zeepooling.
      appspot.com&response_type=code&client_id=1496964127&display=default 
      Then, we use self.redirect() method to call that url, afterward we
      should be able to see/fetch 'code' from:
      http://zeepooling.appspot.com/weibo_login?code=xxyyyzzz111222333
      then we can use this code to request access_token to access user's resource.
      """
      def get(self):
        client = APIClient(app_key=WEIBO_APP_KEY, app_secret=WEIBO_APP_SECRET,
                           redirect_uri=CALLBACK_URL)
        # Compile authorize url for getting 'code'
        url = client.get_authorize_url()  
                            
        # Get authorization 'code' from url return for further access_token.          
        verification_code = self.request.get("code")
        logging.info('Weibo authorization code %s' % verification_code)
        
        if self.request.get("code"):
          code = self.request.get("code")
          logging.info('code is %s' % code)

          # Setup access_token for further user resource accessing.
          r = client.request_access_token(code)
          access_token = r.access_token
          expires_in = r.expires_in
          client.set_access_token(access_token, expires_in)
                 
          # Access user's resource.
          #testing3 = client.get.statuses__user_timeline()
          #testing2 = client.post.statuses__update(status=POST_MY_MESSAGE)
          #testing3 = client.get.statuses__show(id=3440531025750668)
          weibo_uid = client.get.account__get_uid()
          
          # Get user profile info by uid.
          weibo_user_profile = client.get.users__show(uid=weibo_uid.uid)
    
          # Compile profile info as we wanted, and store to WeiboUser entity.
          weibo_id = str(weibo_user_profile.id)
          weibo_profile_url = weibo_user_profile.profile_url
          weibo_profile_image_url = weibo_user_profile.profile_image_url
          weibo_screen_name = weibo_user_profile.screen_name
          
          
          user = WeiboUser(
                     key_name=weibo_id, access_token=access_token, id=weibo_id,
                     profile_url=weibo_profile_url, 
                     profile_image_url=weibo_profile_image_url,
                     screen_name=weibo_screen_name)
          user.put()
          set_cookie(self.response, "weibo_user", str(weibo_id),
                     expires=time.time() + 30 * 86400)
          logging.info('Set Weibo cookie is okay')
          self.redirect("/")
        else:
          logging.info('no code can be found....')
          self.redirect(url)


class LogoutHandler(BaseHandler):
    def get(self):
        set_cookie(self.response, "weibo_user", "", expires=time.time() - 86400)
        self.redirect("/")
            
            
def set_cookie(response, name, value, domain=None, path="/", expires=None):
    """Generates and signs a cookie for the give name/value"""
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(value, timestamp)
    cookie = Cookie.BaseCookie()
    cookie[name] = "|".join([value, timestamp, signature])
    cookie[name]["path"] = path
    
    if domain:
        cookie[name]["domain"] = domain
    if expires:
        cookie[name]["expires"] = email.utils.formatdate(
            expires, localtime=False, usegmt=True)
        
    response.headers.add("Set-Cookie", cookie.output()[12:])


def parse_cookie(value):
    """Parses and verifies a cookie value from set_cookie"""
    if not value:
        return None
    parts = value.split("|")
    if len(parts) != 3:
        return None
    if cookie_signature(parts[0], parts[1]) != parts[2]:
        logging.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 30 * 86400:
        logging.warning("Expired cookie %r", value)
        return None
    try:
        return base64.b64decode(parts[0]).strip()
    except:
        return None
    
          
def cookie_signature(*parts):
    """Generates a cookie signature.

    We use the Weibo app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(WEIBO_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts:
        hash.update(part)
    return hash.hexdigest()