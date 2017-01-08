import requests
import urllib2
import xml.etree.ElementTree as ET

app_key = 'nDxVbWqD6dLp5Zrp'
city_name = '37922'
radius = '10'  # number of miles to search within
#r = requests.get('http://api.eventful.com/rest/events/search?app_key='+app_key+'&location='+city+'&date=Today&within='+radius)
response = urllib2.urlopen('http://api.eventful.com/rest/events/search?app_key='+app_key+'&location='+city_name+'&date=Today&within='+radius)
root = ET.fromstring(response.read())

numberOfEvents = len(root[8])
eid=''
for event in root[8]:
    #print [event.attrib['id'],event.find('title').text.split(':')[0], event.find('description').text, event.find('start_time').text]
    eid = event.attrib['id']
print eid
#print ''
#print 'There are ' + str(len(root[8])) + ' events going on in ' + city_name + ' today.'

response = urllib2.urlopen('http://api.eventful.com/rest/events/get?app_key='+app_key+'&id=' + eid)
root = ET.fromstring(response.read())

#print root.find('description').text
