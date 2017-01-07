import requests
import xml.etree.ElementTree as ET

app_key = 'nDxVbWqD6dLp5Zrp'
city = 'Raleigh'
radius = '10'  # number of miles to search within
r = requests.get('http://api.eventful.com/rest/events/search?app_key='+app_key+'&location='+city+'&date=Today&within='+radius)
root = ET.fromstring(str(r.content))

numberOfEvents = len(root[8])
for event in root[8]:
    print [event.find('title').text, event.find('description').text, event.find('start_time').text]

print ''
print 'There are ' + str(len(root[8])) + ' events going on in ' + city + ' today.'
