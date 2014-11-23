
xml = """<HostipLookupResultSet xmlns:gml="http://www.opengis.net/gml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0.1" xsi:noNamespaceSchemaLocation="http://www.hostip.info/api/hostip-1.0.1.xsd">
           <gml:description>This is the Hostip Lookup Service</gml:description>
           <gml:name>hostip</gml:name>
           <gml:boundedBy>
             <gml:Null>inapplicable</gml:Null>
           </gml:boundedBy>
           <gml:featureMember>
             <Hostip>
               <ip>12.215.42.19</ip>
               <gml:name>Aurora, TX</gml:name>
               <countryName>UNITED STATES</countryName>
               <countryAbbrev>US</countryAbbrev>
               <!-- Co-ordinates are available as lng,lat -->
               <ipLocation>
                 <gml:pointProperty>
                   <gml:Point srsName="http://www.opengis.net/gml/srs/epsg.xml#4326">
                     <gml:coordinates>-97.5159,33.0582</gml:coordinates>
                   </gml:Point>
                 </gml:pointProperty>
               </ipLocation>
             </Hostip>
           </gml:featureMember>
        </HostipLookupResultSet>"""

# QUIZ - implement the get_coords(xml) function that takes in an xml string
# and returns a tuple of (lat, lon) if there are coordinates in the xml.
# Remember that you should use minidom to do this.
# Also, notice that the coordinates in the xml string are in the format:
# (lon,lat), so you will have to switch them around.

from xml.dom import minidom

def get_coords(xml):
    dom = minidom.parseString(xml)
    coordNode = dom.getElementsByTagName("gml:coordinates")        # returns a list of nodes; the text
    if len(coordNode) > 0:                                         # is in a child text node
    	lon, lat = coordNode[0].firstChild.nodeValue.split(',')
    	return (lat,lon)
    return

# print "Coordinates are:", get_coords(xml)
# version developed in the class lectures using the API on the hostip.info website to get latitude and longitude
# of an IP address
IP_URL = "http://api.hostip.info/?ip="
from xml.dom import minidom                   # built-in library for XML DOM manipulation
import urllib2                                # built-in library to fetch web pages

def get_coords(ip):
	url = IP_URL + ip
	content = None
	try:
		content = urllib2.urlopen(url).read()
	except URLError:
		return

	if content:
    	dom = minidom.parseString(xml)
    	coordNode = dom.getElementsByTagName("gml:coordinates")        # returns a list of nodes; the text
    	if len(coordNode) > 0 and coordNode[0].firstChild.nodeValue:                                         # is in a child text node
    		lon, lat = coordNode[0].firstChild.nodeValue.split(',')
    		return db.GeoPt(lat,lon)          # use GDS built-in class for geolocation
    return

from collections import namedtuple

# make a basic Point class
Point = namedtuple('Point', ["lat", "lon"])
points = [Point("1","2"),
          Point("3","4"),
          Point("5","6")]

# QUIZ - implement the function gmaps_img(points) that returns the google maps image
# for a map with the points passed in. A example valid response looks like
# this:
#
# http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&markers=1,2&markers=3,4
#
# Note that you should be able to get the first and second part of an individual Point p with
# p.lat and p.lon, respectively, based on the above code. For example, points[0].lat would
# return 1, while points[2].lon would return 6.

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"

def gmaps_img(points):
	markers = '&'.join(["markers=%s,%s" % (point.lat, point.lon) for point in points])
	return GMAPS_URL + markers

print gmaps_img(points)
