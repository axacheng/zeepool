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

""" This code is changed by Axa for WeiBo Oauth2.0 testing.

Original author is https://github.com/martey
http://github.com/pythonforfacebook/facebook-sdk
http://pypi.python.org/pypi/facebook-sdk/0.3.0

Please make sure you have oauth2.0.html and app.yaml these files for test run.
oauth2.0.html is web page for this testing code.
app.yaml is GAE config file.

*****************
* oauth2.0.html *
*****************
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <title>WeiBo OAuth2.0 login testing</title>
  </head>
  
  <body>
    <p> WeiBo login </p>
    <p><a href="/weibo_login">Log in with WeiBooooooo</a></p>
    <pre>
    WeiBo python SDK:廖雪峰
    http://code.google.com/p/sinaweibopy/source/browse/src/weibo.py
    
    My testing code:
    https://code.google.com/p/zeepool/source/browse/src/weibo_oauth2_test.py
    
    Testing weibo posting page:
    But I have to change GAE default version to 3
    http://axa.appspot.com/ 
    
    Testing weibo show user profile page:
    But I have to change GAE default version to 4
    http://axa.appspot.com/
    
    Testing result here:
    http://www.weibo.com/u/1861651780
    </pre>
  </body>
</html>


************
* app.yaml *
************
application: axa
version: 4
runtime: python
api_version: 1

handlers:
- url: /.*
  script: weibo_oauth_v2.py

"""

import logging
import os.path
from weibo import APIClient

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template


class WeiBoLogin(webapp.RequestHandler):
      """ WeiBo APIClient login testing.
      
      When user first time to get in our site, they should request 'code'
      by using url=client.get_authorize_url() to compile URL e.g.:
      https://api.weibo.com/oauth2/authorize?redirect_uri=http%3A//axa.
      appspot.com&response_type=code&client_id=1496964127&display=default 
      Then, we use self.redirect() method to call that url, afterward we
      should be able to see/fetch 'code' from:
      http://axa.appspot.com/weibo_login?code=xxyyyzzz111222333
      then we can use this code to request access_token to access user's resource.
      """
      def get(self):
        APP_KEY='1496964127'
        APP_SECRET='ec756023d85cd93846a7fe52d7b6d784'
        
        # This CALLBACK_URL must be the same as :
        # http://open.weibo.com/apps/1496964127/info/advanced
        # 裡面的 "应用回调页" Otherwise, you would get 'error:redirect_uri_mismatch'
        CALLBACK_URL='http://axa.appspot.com/weibo_login'  
        
        # (NOTE) PLEASE CHANGE POST_MY_MESSAGE text BEFORE RUN THIS CODE!!!
        # WeiBo would treat you as spam (duplicate is not allowed!) so you would
        # get Server 500 error (aka: 400 Bad Gateway on weibo end).
        POST_MY_MESSAGE = 'haha, 這是我最後的測試'


        client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET,
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
          weibo_user_profile = client.get.users__show(uid=weibo_uid.uid)
    
          username = weibo_user_profile.screen_name
          userimage = weibo_user_profile.profile_image_url
          self.response.out.write('<h1>My WeiBo username is: <font color="blue">%s</font></h1> <img src="%s">' % (
              username, userimage))

          #self.response.out.write(weibo_user_profile)

        else:
          logging.info('no code can be found....')
          self.redirect(url)
        
      
class HomeHandler(webapp.RequestHandler):
    def get(self):
      args = ''
      path = os.path.join(os.path.dirname(__file__), "oauth2.0.html")
      self.response.out.write(template.render(path, args))


def main():
    util.run_wsgi_app(webapp.WSGIApplication([
        (r"/", HomeHandler),
        (r"/weibo_login", WeiBoLogin),
    ]))


if __name__ == "__main__":
    main()
