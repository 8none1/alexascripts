"""
Talk to the Myth Proxy which in turn talks to Myth TV.
Will allow for setting of recordings, cancelling exising recordings
and eventually some controls like "off" "mute" and maybe even "play programme"
"""

from __future__ import print_function
import requests
import secrets
import datetime

myth_endpoint = secrets.endpoint
username = secrets.username
password = secrets.password
cert = "selfcert.pem"
appid = None


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hello!  Please tell me the title and channel of the programme you would like to record."
    reprompt_text = "Tell me the programme and channel for the recording.  For example say, record Blue Peter on CBBC."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Good bye!"
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def dispatch_request(title, channel,appid): #, session):
    auth = requests.auth.HTTPBasicAuth(username,password)
    data = data={'title':title, 'channel':channel, 'appid':appid}
    r = requests.post(myth_endpoint, data=data, auth = auth, verify=cert) # verify = False
    if r.status_code == 200:
        return r.json()
    else:
        return False

def record_programme(intent, session,appid):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    title = None
    channel = None
    
    if 'ProgrammeTitles' in intent['slots']:
        title = intent['slots']['ProgrammeTitles']['value']

    if 'ChannelNames' in intent['slots']:
        channel = intent['slots']['ChannelNames']['value']
    
    if title is not None and channel is not None:
        data = dispatch_request(title, channel,appid)
        if data is not None and data['status'] == True:
            title = data['title']
            descr = data['description']
            starttime = data['start_time']
            message = data['message']
            speech_output = "OK! " + title + ".  " + descr + "."
            reprompt_text = None
            should_end_session = True
        else:
            speech_output = "Sorry, I couldn't record that programme.  Please try again."
            reprompt_text = "Are you still there?"
            should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    appid = session['application']['applicationId']

    # Dispatch to your skill's intent handlers
    if intent_name == "RecordProgrammeIntent":
        return record_programme(intent, session,appid)
    elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    appid = event['session']['application']['applicationId']
    if appid != "amzn1.ask.skill.e0d39143-ebe0-40da-b7fa-babba8eba719":
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


