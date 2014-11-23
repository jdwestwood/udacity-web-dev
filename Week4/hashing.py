import hashlib
import hmac

# Implement the hash_str function to use HMAC and our SECRET instead of md5
SECRET = 'imsosecret'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

#def hash_str(s):
#    return hashlib.md5(s).hexdigest()

# -----------------
# User Instructions
#
# Implement the function make_secure_val, which takes a string and returns a
# string of the format:
# s,HASH

def make_secure_val(s):
#    return s + "," + hash_str(s)
	return "%s|%s" % (s, hash_str(s))      # class sol'n (using a , as the separator breaks Google App Engine)
print make_secure_val("Hello")

# -----------------
# User Instructions
#
# Implement the function check_secure_val, which takes a string of the format
# s,HASH
# and returns s if hash_str(s) == HASH, otherwise None

def check_secure_val(h):
    s, hash_s = h.split("|")
    if hash_str(s) == hash_s:
    	return s
    else:
    	return None

hashed = make_secure_val("Hello")
print check_secure_val(hashed)
print hash_str("Hello")

import random
import string

# implement the function make_salt() that returns a string of 5 random
# letters use python's random module.
# Note: The string package might be useful here.

random.seed()
def make_salt():
    return "".join([random.choice(string.ascii_letters) for i in xrange(5)])

for i in range(5):
	print make_salt()

# implement the function make_pw_hash(name, pw) that returns a hashed password
# of the format:
# HASH(name + pw + salt),salt
# use sha256

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
    return "%s,%s" % (hashlib.sha256(name + pw + salt).hexdigest(), salt)

print make_pw_hash("westwood", "password")

# Implement the function valid_pw() that returns True if a user's password
# matches its hash. You will need to modify make_pw_hash.

def valid_pw(name, pw, h):
    hash_val, salt = h.split(',')
    return hashlib.sha256(name + pw + salt).hexdigest() == hash_val

h = make_pw_hash('spez', 'hunter2')
print valid_pw('spez', 'hunter2', h)

