#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import datetime
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users

bkleong_key = ndb.Key('BKLeong', 'default_bkleong')

import bkutils, socket
keylevel, element = bkutils.loadCsv()

class BkLeong(ndb.Model):
  author  = ndb.UserProperty()
  source  = ndb.TextProperty()
  content = ndb.TextProperty()
  date    = ndb.DateTimeProperty(auto_now_add=True)

def process(self):
  try: 
    currentlevel = int(self.request.get('level', '1'))
    nextlevel = currentlevel+1
  except: 
    currentlevel = 1
    nextlevel    = 2

  debug = True if 'debug' in self.request.arguments() else False

  self.response.out.write('<html><body>\n')
  self.response.out.write('<form action="/bksubmit" method="post">\n')
  self.response.out.write('<input type=hidden name="level" value="%s">\n'%nextlevel)
  if debug: self.response.out.write('<input type=hidden name="debug" value="true">\n')

  for level in keylevel:

    if debug: self.response.out.write('<br/>Level %s: <br/>\n'%level)
    elif level > currentlevel: continue

    has_button=False
    for comp in element[level]:
      if debug or level == currentlevel:
        self.response.out.write(comp[2]+'<br/>\n')
        if comp[0].strip().lower()=='button': has_button=True
      elif level < currentlevel:
        compname = self.request.get(comp[1])
        if compname: 
          self.response.out.write('<input type=hidden name="%s" value="%s">\n'%(compname,compname))

    if level == currentlevel and not has_button: 
      self.response.out.write('<input type=submit value="submit"><br/>\n')

  self.response.out.write('</form></body></html>\n')

class MainPage(webapp2.RequestHandler):
  def get(self):
    #import urllib2
    #response = urllib2.urlopen('https://dl.dropboxusercontent.com/s/fzsidpfxf4h4r1g/bkleong.html')
    #html = response.read()
    #self.response.out.write(html)
    process(self)

class BkSubmit(webapp2.RequestHandler):
  def post(self):

    try   : currentlevel = int(self.request.get('level', '1'))
    except: currentlevel = 1
    debug = True if 'debug' in self.request.arguments() else False

    if not debug and currentlevel <= keylevel[-1]: 
      process(self)
      return

    client_ip = self.request.remote_addr
    self.response.out.write('Selection by [%s]: <br/>\n'%client_ip)

    userselection = []
    for level in keylevel:
      for comp in element[level]:
        compname = self.request.get(comp[1])
        if compname: userselection.append(compname)

    userselection = bkutils.printCsv(userselection)
    self.response.out.write(userselection + '<br/>\n')

    #return
    bk = BkLeong(parent=bkleong_key)

    if users.get_current_user():
      bk.author = users.get_current_user()

    bk.source  = client_ip
    bk.content = userselection
    bk.put()
    #self.redirect('/')

class BkView(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')

    bkdata = ndb.gql('SELECT * '
                     'FROM BkLeong '
                     'WHERE ANCESTOR IS :1 '
                     'ORDER BY date DESC LIMIT 100',
                     bkleong_key)

    for row in bkdata:
      self.response.out.write('<b>%s</b> on <b>%s</b> submitted:' % (row.source, row.date))
      self.response.out.write('<blockquote>%s</blockquote>' %
                              cgi.escape(row.content))

    self.response.out.write('</body></html>')


app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/bkview', BkView),
  ('/bksubmit', BkSubmit)
], debug=True)



