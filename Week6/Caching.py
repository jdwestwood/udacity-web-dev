import time

# complex_computation() simulates a slow function. time.sleep(n) causes the
# program to pause for n seconds. In real life, this might be a call to a
# database, or a request to another web service.
def complex_computation(a, b):
    time.sleep(.5)
    return a + b

# QUIZ - Improve the cached_computation() function below so that it caches
# results after computing them for the first time so future calls are faster
cache = {}
def cached_computation(a, b):
  tryCache = cache.get((a,b))
  if tryCache:
    return tryCache
  else:
    newCache = complex_computation(a, b)
    cache[(a,b)] = newCache
    cache[(b,a)] = newCache
    return newCache

start_time = time.time()
print cached_computation(5, 3)
print "the first computation took %f seconds" % (time.time() - start_time)

start_time2 = time.time()
print cached_computation(5, 3)
print "the second computation took %f seconds" % (time.time() - start_time2)

# QUIZ - load balancing simulation
#handy link
#http://stackoverflow.com/questions/423379/using-global-variables-in-a-function-other-than-the-one-that-created-them
#maybe a link to itertools

servers = ['SERVER1', 'SERVER2', 'SERVER3', 'SERVER4']

# QUIZ - implement the function get_server, which returns one element from the
# list SERVERS in a round-robin fashion on each call. Note that you should
# comment out all your 'print get_server()' statements before submitting
# your code or the grading script may fail. For more info see:
# http://forums.udacity.com/cs253-april2012/questions/22327/unit6-13-quiz-problem-with-submission

n = -1
def get_server():
    global n
    n += 1
    server = n % len(servers)
    return servers[server]

print get_server()
print get_server()
print get_server()
print get_server()
print get_server()
print get_server()
print get_server()
print get_server()


# QUIZ implement the basic memcache functions

CACHE = {}

#return True after setting the data
def set(key, value):
    CACHE[key] = value
    return True

#return the value for key
def get(key):
    return CACHE.get(key)

#delete key from the cache
def delete(key):
  if key in CACHE:
    del CACHE[key]

#clear the entire cache
def flush():
    CACHE.clear()

print set('x', 1)
#>>> True

print get('x')
#>>> 1

print get('y')
#>>> None

delete('x')
print get('x')
#>>> None

# QUIZ - implement gets() and cas() below
#return a tuple of (value, h), where h is hash of the value. a simple hash
#we can use here is hash(repr(val))

import hashlib

def gets(key):
    cur_val = get(key)
    if cur_val:
      return (cur_val, hash(repr(cur_val)))
    else:
      return (None, None)

# set key = value and return True if cas_unique matches the hash of the value
# already in the cache. if cas_unique does not match the hash of the value in
# the cache, don't set anything and return False.
def cas(key, value, cas_unique):
    cur_val, cur_uniq = gets(key)
    if cur_val:
      if cas_unique == cur_uniq:
        return set(key,value)
      else:
        return False
    else:
      return set(key,value)


print set('x', 1)
#>>> True
#
print get('x')
#>>> 1
#
print get('y')
#>>> None
#
delete('x')
print get('x')
#>>> None
#
set('x', 2)
print gets('x')
#>>> 2, HASH
#
print cas('x', 3, 0)
#>>> False
#
print cas('x', 4, gets('x')[1])
#>>> True
#
print get('x')
#>>> 4
