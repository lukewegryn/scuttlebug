import urllib2
import xml.etree.ElementTree as ET

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
    else:
        return get_error()

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def get_scuttlebug(intent):
    session_attributes = {}
    card_title = "Scuttlebug Events"
    speech_output = "I'm not sure which city you wanted the Scuttle Bug for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which city you wanted the Scuttle Bug for. "
    should_end_session = False

    print intent["slots"]["City"]["name"]
    if "City" in intent["slots"]["City"]["name"]:
        print "Found Raleigh"
        city_name = intent["slots"]["City"]["value"]
        app_key = 'nDxVbWqD6dLp5Zrp'
        radius = '10'  # number of miles to search within
        response = urllib2.urlopen('http://api.eventful.com/rest/events/search?app_key='+app_key+'&location='+city_name+'&sort_order=popularity&date=Today&within='+radius)
        root = ET.fromstring(response.read())

        numberOfEvents = len(root[8])
        state = root[8][0].find('region_name').text
        speech_output = 'There are ' + str(len(root[8])) + ' events going on in ' + city_name + ', ' + state + ' today. '
        counter = 1
        for event in root[8]:
            speech_output += '' + str(counter) + '. ' + event.find('title').text.split(':')[0] + '. ' 
             #[event.find('title').text.split(':')[0], event.find('description').text, event.find('start_time').text]
            counter += 1
        
        reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
card_title, speech_output, reprompt_text, should_end_session))

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