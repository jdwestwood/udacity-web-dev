#!/usr/bin/env python
# appcfg.py rollback C:\Udacity\Web_dev\Week3\jdw-blog\jdw-blog to rollback the website on GAE
# Follow the weeks 3, 4 lecture notes for the general construction of this website
# deployed site at jdw-blog.appspot.com
#
import os          # python module for operating system tasks
import logging     # python module for debugging
import time
#from datetime import datetime    # python module for date and time manipulation
import webapp2
import jinja2      # python html templating; modify app.yaml so Google App Engine knows we will be using it
import random      # python built-in module
import string      # python built-in module
import hashlib     # python built-in module
import hmac        # python built-in module
import json        # python built-in module
from google.appengine.ext import db
from google.appengine.api import memcache

memClient = memcache.Client()

random.seed()      # initialize the random number generator (with the system time)

# the following functions were developed in the Week 4 lectures.  See \Week4\hashing.py
# use hash_str, make_secure_val, and check_secure_val to send and verify secure cookies
SECRET = 'blogSite248221'
def hash_str(s):
	# use hmac (Hash-based Message Authentication Code) for the encrypted part of cookies
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
	# takes a string s and returns a string of the format s|HASH(s) to send as a cookie
	return "%s|%s" % (s, hash_str(s))   # (using a , as the separator breaks Google App Engine)

def check_secure_val(h):
	# takes a string h of the form s|HASH(s) from a cookie and checks if HASH(s) is the
	# hash of s; make sure the cookie has not been tampered with.
    s, hash_s = h.split("|")
    if hash_str(s) == hash_s:
    	return s
    else:
    	return None

# use make_salt, make_pw_hash, and valid_pw to encrypt and check user passwords in the Users db
def make_salt():
	# return a string of 5 random letters; requires the python random and string modules
    return "".join([random.choice(string.ascii_letters) for i in xrange(5)])

def make_pw_hash(name, pw, salt=None):
	# return a string consisting of the sha256 hash of username + pw + salt, salt to store
	# encrypted in the User database
	if not salt:
		salt = make_salt()
	return "%s,%s" % (hashlib.sha256(name + pw + salt).hexdigest(), salt)

def valid_pw(name, pw, h):
	# return True if the hashed name + pw matches the hash_val; h has the form hash_val, salt
    hash_val, salt = h.split(',')
    return make_pw_hash(name, pw, salt) == h

def fmt_datetime(GDS_datetime):
	# format a Google App Engine Datastore DateTime, which is a Python datetime object, used in the jinja template
	return GDS_datetime.strftime('%a %b %d %Y %I:%M:%S %p')   # Wed Apr 20 1957 08:30:21 PM

# documentation for Jinja2 at jinja.pocoo.org/docs/
# create jinja environment: tell jinja where template files are; jinja will escape
# all special HTML characters when sending output
template_dir = os.path.join(os.path.dirname(__file__), 'templates')  # put html in templates subdirectory of this project
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	                           autoescape = True)
jinja_env.filters['fmt_datetime'] = fmt_datetime   # to be able to call Python function from the html template

class Users(db.Model):
	username = db.StringProperty(required=True)
	hash_user_pw_salt = db.StringProperty(required=True)

class BlogEntry(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	date_time = db.DateTimeProperty(auto_now_add = True)

def makeBlogEntryDict(blog_entry):
	# makes a dictionary object from BlogEntry blog_entry to be dumped to JSON
	return {"subject" : blog_entry.subject,
			"content": blog_entry.content,
			"created": fmt_datetime(blog_entry.date_time)}

def getBlogEntryInfoByID(blog_entry_id):
	# get the BlogEntry whose id is the string blog_entry_id, either from cache or DB
	blog_entry_info = memClient.get(blog_entry_id)
	if not blog_entry_info:   # this branch only called for permalinks that already existed when permalink caching was added
		logging.info("Getting blog entry from BlogEntry DB model")
		blog_entry = BlogEntry.get_by_id(int(blog_entry_id))
		updatePermalinkCache(blog_entry_id, blog_entry)
		blog_entry_info = memClient.get(blog_entry_id)
	return blog_entry_info

def updatePermalinkCache(blog_entry_id, blog_entry):
	# update the cache of permalinks; do not use .gets or .cas since permalink data is never changed
	# blog_entry_id must be a string; blog_entry is a BlogEntry entity
	blog_entry_info = dict({"blog_entry": blog_entry, "created": time.time()})
	memClient.set(blog_entry_id, blog_entry_info)

def getBlogEntries():
	# return the 10 most recent blog entries as a list of BlogEntry's ordered in descending date order
    blog_entries = memClient.get("main")
    if not blog_entries:
    	logging.info("Querying DB")
    	blog_entries = db.GqlQuery("SELECT * FROM BlogEntry ORDER BY date_time DESC LIMIT 10")
    	# the query only runs when blog_entries is used in some way; prevent running the query more
    	# than once by putting the results into a list and then using the list multiple times.
    	blog_entries = list(blog_entries)
    	memClient.set("main", blog_entries)
    	memClient.set("last_access", time.time())
    return blog_entries

def updateMainPageCache(blog_entry):
	# update the cache with a single blog entry; use .gets and .cas to make sure we are not overwriting
	# simultaneously occurring updates. The 'unique' value for a key,value is tracked internally by
	# the memcache.Client object
	updated = False
	i = 0
	while not updated and i < 100:
		i += 1
		blog_entries = memClient.gets("main")
		if blog_entries:
			if len(blog_entries) > 10:
				blog_entries.pop()                 # remove the least recent entry
		else:
			blog_entries = list()
		blog_entries.insert(0, blog_entry)     # insert the POSTed entry at the head of the list
		updated = memClient.cas("main", blog_entries)
	if updated:
		return True
	else:
		logging.info("Memcache update failed")
		return False

class Handler(webapp2.RequestHandler):     # Handler inherits from webapp2.RequestHandler
    def render_str(self, templateFile, **params):
    	t = jinja_env.get_template(templateFile)
    	return t.render(params)

    def render(self, templateFile, **key_val_pairs):
    	renderedText = self.render_str(templateFile, **key_val_pairs)
    	self.response.out.write(renderedText)

class MainPage(Handler):                   # MainPage inherits from Handler
    def get(self, version=""):
    	blog_entries = getBlogEntries()
    	if version:
    		logging.info("Here None")
    		if version.lower() == "json":
    			blog_entries_obj = [makeBlogEntryDict(blog_entry) for blog_entry in blog_entries]
    			blog_entries_json = json.dumps(blog_entries_obj)
    			self.response.headers["Content-Type"] = "application/json"
    			self.response.out.write(blog_entries_json)
    	else:
    		elapsed_time = "%1.0f" % (time.time() - memClient.get("last_access"))
    		self.render("blogpage.html", blog_entries=blog_entries, elapsed_time=elapsed_time)

class NewPostPage(Handler):
	def render_newpost(self, subject="", content="", error=""):   # argument values default to empty string
		self.render("newpost.html", subject=subject, content=content, error=error) # template parameter = function argument

	def get(self):
		self.render_newpost()

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:
			blog_entry = BlogEntry(subject=subject, content=content) # db entity name = form entry value
			blog_entry.put()                       # add to the database
			blog_entry_id = str(blog_entry.key().id()) # get id of the entity in the Datastore; convert int to string
			updateMainPageCache(blog_entry)
			updatePermalinkCache(blog_entry_id, blog_entry)
			permalink_uri = self.uri_for('permalink_page', post_id=blog_entry_id)
			self.redirect(permalink_uri)            # go to the permalink page
		else:
			error = "Please enter both a subject and a blog entry"
			self.render_newpost(subject, content, error)          # function argument = form entry value

class SignupPage(Handler):
	def render_signup(self, username="", password="", verify="", email="",
	                  error_username="", error_password="", error_verify="", error_email=""):  # argument values default to empty string
		self.render("register.html", username=username, password=password, verify=verify, email=email,
		             error_username=error_username, error_password=error_password,
		             error_verify=error_verify, error_email=error_email)   # template parameter = function argument

	def get(self):
		self.render_signup()

	def post(self):
		username = self.request.get("username")  # name= in the form
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")
		error_username = ""
		error_password = ""
		error_verify = ""
		error_email = ""
		resend = False

		if username:
			user = db.GqlQuery("SELECT * FROM Users WHERE username='%s'" % username).get()
			if user:
				resend = True
				error_username = "User '" + user.username + "' already exists. Please choose a different username"
				username = ""
		else:
			resend = True
			error_username = "Please choose a username"

		if password and verify:
			if verify != password:
				resend = True
				verify = ""
				error_verify = "Passwords did not match. Please re-enter your password"
		else:                         # one or more password inputs blank; send the form again with error messages
			resend = True
			if not password:
				error_password = "Please choose a password"
			if not verify:
				error_verify = "Please re-enter your password"
		if resend:
			self.render_signup(username, password, verify, email, error_username, error_password,
			                   error_verify, error_email)          # function argument = form entry value
		else:
			hash_user_pw_salt = make_pw_hash(username, password)   # hash username and password with added salt
			users_entry = Users(username=username, hash_user_pw_salt=hash_user_pw_salt)
			users_entry.put()                        # add to the database
			users_entry_id = str(users_entry.key().id())  # get id of the entity for this user in the Datastore to send in a cookie
			users_entry_id_hash = make_secure_val(users_entry_id)
			self.response.set_cookie('users_entry_id', value=users_entry_id_hash, path='/')
			self.redirect('/welcome')                # go to the welcome page

class WelcomePage(Handler):
	def get(self):
		users_entry_cookie = self.request.cookies.get('users_entry_id')
		if users_entry_cookie:                           # Welcome page loaded by registered user
			users_entry_id = check_secure_val(users_entry_cookie)  # decode the cookie to get the id of the entity for this user
			if users_entry_id:                           # if it hasn't been tampered with
				user = Users.get_by_id(int(users_entry_id))
				self.render("welcome.html", username=user.username)
				return
			else:
				self.response.delete_cookie('users_entry_id')
		self.render("welcome.html")      # Welcome page loaded by non-logged in user

class PermalinkPage(Handler):
	def get(self, post_id, version=None):          # post_id is passed as a result of defining <post_id> template in the routing table
		blog_entry_info = getBlogEntryInfoByID(post_id)  # post_id is a string
		if blog_entry_info:
			blog_entry = blog_entry_info.get("blog_entry")
			elapsed_time = "%1.0f" % (time.time() - blog_entry_info.get("created"))
			if version:
				if version.lower() == "json":          # JSON
					blog_entry_dict = makeBlogEntryDict(blog_entry)
					blog_entry_json = json.dumps(blog_entry_dict)
					self.response.headers["Content-Type"] = "application/json"
					self.response.out.write(blog_entry_json)
			else:                                  # normal HTML
				self.render("permalink.html", subject=blog_entry.subject, content=blog_entry.content,
				      date_time=blog_entry.date_time, elapsed_time=elapsed_time)

class FlushPage(Handler):
	def get(self):
		memClient.flush_all()
		self.redirect('/')

app = webapp2.WSGIApplication(routes=[
    ('/', MainPage),
    ('/newpost', NewPostPage),
    ('/signup', SignupPage),
    ('/welcome', WelcomePage),
    ('/flush', FlushPage)
], debug=True)
app.router.add(webapp2.Route(r'/.<version:json(?i)>', handler=MainPage, name='main_page_json')) # name the route so can use templating in webapp2.uri_for() if needed
app.router.add(webapp2.Route(r'/<post_id:\d+>', handler=PermalinkPage, name='permalink_page'))  # name the route so can use templating in webapp2.uri_for()
app.router.add(webapp2.Route(r'/<post_id:\d+>.<version:json(?i)>', handler=PermalinkPage, name='permalink_page_json'))  # name the route so can use templating in webapp2.uri_for() if needed
