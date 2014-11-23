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
import webapp2
import cgi         # to use cgi.escape() to escape HTML special characters

htmlContent="""
<!DOCTYPE html>
<html>
<body>
<h2>Enter some text to ROT13:</h2>
<form method="post" action="/rot13">
	<div>
		<textarea name="text" style="width: 600px; height: 200px;">%(textContent)s</textarea>
	</div>
	<div>
		<input type="submit" value="Submit">
	</div>
</form>
</body>
<html>
"""

def rot13(inText):
	origAlpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
	rot13Alpha = "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
	outText = ""
	for char in inText:
		origIndex = origAlpha.find(char)
		if origIndex != -1:
			outText += rot13Alpha[origIndex]
		else:
			outText += char
	return cgi.escape(outText)

inText = ""
redirected = False

class MainHandler(webapp2.RequestHandler):
    def get(self):
    	global inText, redirected
    	if not redirected:
    		inText = ""
    	else:
    		redirected = False
    	self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(htmlContent % {"textContent" : rot13(inText)})

class TestHandler(webapp2.RequestHandler):
	def post(self):
		global inText, redirected
		redirected = True
		inText = self.request.get("text")
		self.redirect("/")
#		outText = rot13(inText)
#   	self.response.headers['Content-Type'] = 'text/html'
#		self.response.out.write(htmlContent % {"textContent" : outText})
#		self.response.headers['Content-Type'] = 'text/plain'
#		self.response.out.write(self.request)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/rot13', TestHandler)
], debug=True)

