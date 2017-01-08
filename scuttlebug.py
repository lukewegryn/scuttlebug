import urllib2
import xml.etree.ElementTree as ET

app_key = 'nDxVbWqD6dLp5Zrp'

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.27a38ff5-cb81-4ecc-b4ad-4e297fdfc5fa"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])
    
def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "WhatsTheScuttleBugIntent":
        return get_scuttlebug(intent)
    elif intent_name == "EventDetailsIntent":
        return get_event_detail(intent,session)
    else:
        return get_error()

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def get_scuttlebug(intent):
    session_attributes = {}
    card_title = "Scuttlebug Events"
    speech_output = "Say something like, 'What\'s up in Raleigh. " 
    reprompt_text = "Say something like, 'What\'s up in Raleigh. "
    should_end_session = False
    radius = '10'  # number of miles to search within
    
    if "value" in intent["slots"]["City"]:
        city_id = intent["slots"]["City"]["value"].replace(" ","+")
    elif "value" in intent["slots"]["ZipCode"]:
        city_id = str(intent["slots"]["ZipCode"]["value"])
        
    response = urllib2.urlopen('http://api.eventful.com/rest/events/search?app_key='+app_key+'&sort_direction=descending&location='+city_id+'&sort_order=popularity&page_size=50&date=Today&within='+radius)
    root = ET.fromstring(response.read())

    max_events = 5
    numberOfEvents = max_events
    if len(root[8]) < max_events:
        numberOfEvents = len(root[8])
    state = root[8][0].find('region_name').text
    city = root[8][0].find('city_name').text
    speech_output = 'Here are the ' + str(numberOfEvents) + ' most popular events going on in ' + city + ', ' + state + ' today.\n '
    counter = 1
    for event in root[8]:
        speech_output += '' + str(counter) + '. ' + event.find('title').text.split(':')[0] + '.\n ' 
         #[event.find('title').text.split(':')[0], event.find('description').text, event.find('start_time').text]
        session_attributes[counter]=event.attrib['id'].split('@')[0]
        if counter == max_events:
            break
        counter += 1
        
    
    speech_output += "To learn more about a specific event, say something like 'Tell me more about event number 3'."
        
    reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
card_title, speech_output, reprompt_text, should_end_session))

def get_event_detail(intent,session):
    session_attributes = {}
    reprompt_text = None
    should_end_session = True
    speech_output = ""
    if "value" in intent["slots"]["EventNumber"]:
        event_number = intent["slots"]["EventNumber"]["value"]
        if str(event_number) in session.get('attributes',{}):
            eid = session['attributes'][str(event_number)]
            response = urllib2.urlopen('http://api.eventful.com/rest/events/get?app_key='+app_key+'&id=' + eid)
            root = ET.fromstring(response.read())
            speech_output = "Here are the details for event number " + str(event_number) + ".\n "
            if root.find('title').text:
                speech_output += "Name: " + root.find('title').text + ".\n "
            if root.find('description').text:
                try:
                    tree = ET.fromstring(root.find('description').text)
                    description_notags = ET.tostring(tree, encoding='utf8', method='text')
                    speech_output += "Description: " + description_notags + ". "
                except:
                    speech_output += "Description: " + root.find('description').text + ".\n "
            if root.find('venue_name').text:
                speech_output += "Venue Name: " + root.find('venue_name').text + ".\n "
            if root.find('start_time').text:
                speech_output += "Start Time: " + root.find('start_time').text + ".\n "
            speech_output += "To review the details for this event, look at the Scuttle Bug card in the Alexa App."
    
    return build_response(session_attributes, build_speechlet_response(
            intent['name'], speech_output, reprompt_text, should_end_session))

    
def get_error():
    session_attributes = {}
    card_title = "Scuttle Bug"
    reprompt_text = ""
    should_end_session = False

    speech_output = "I'm sorry, I don't understand that."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_welcome_response():
    session_attributes = {}
    card_title = "Scuttle Bug"
    speech_output = "Welcome to Scuttle Bug. " \
                    "You can ask me, What's the Scuttle Bug in Atlanta?, " \
                    " or, What's up in San Francisco?"
    reprompt_text = "Please ask me, What's the Scuttle Bug in Atlanta?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
card_title, speech_output, reprompt_text, should_end_session))

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
}

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
}