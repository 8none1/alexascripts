#!/usr/bin/python

import MythTV
import os
import sys
import datetime
import cgi
import json
import commander_data

#import cgitb

#cgitb.enable()

sim = True
debug = True
# Probably need to change this depending on what we get from Alexa
chan_lookup={'bbc1':'BBC One', 'bbc2':'BBC Two', 'bbc4':'BBC FOUR',
             '5star':'5*', '5star+1':'5* +1', 'channel4+1':'Channel 4+1', 'channel5':'Channel 5',
             'channel5+1':'Channel 5+1', 'e4':'E4','e4+1':'E4+1', 'more4':'More4', 'channel4':'Channel 4',
             'cbbc':'CBBC'
            }

db = MythTV.MythDB(DBHostName="localhost", DBName="mythconverg", DBUserName="mythtv", DBPassword=commander_data.dbpass)

def search_guide(title, channel):
  progs = db.searchGuide(fuzzytitle=title, callsign=channel, startafter=datetime.datetime.now())
  try:
    progs = progs.next()
    return progs
  except StopIteration:
    return None

def set_recording(guide):
  if not sim:
    rec = MythTV.Record.fromGuide(guide, MythTV.Record.kAllRecord)
    
  
print "Content-Type: application/json"
print


if "REQUEST_METHOD" in os.environ.keys() and os.environ['REQUEST_METHOD'] == "POST":
    form = cgi.FieldStorage()
    title = form["title"].value
    channel = form["channel"].value
    if channel in chan_lookup.keys():
      channel = chan_lookup[channel]
elif "REQUEST_METHOD" in os.environ.keys() and os.environ['REQUEST_METHOD'] is not "POST":
    # Unsupported method.
    print '{"status":false}'
    sys.exit()
else:
    # Here for cli testing only.  Can be removed or commented out later
    title = "Blue Peter"
    channel = "CBBC"

prog = search_guide(title, channel)
response_dict = {}
if prog is not None:
  set_recording(prog)
  response_dict['status'] = True
  response_dict['title'] = prog.get('title')
  response_dict['description'] = prog.get('description')
  starttime = prog.get("starttime")
  starttime = starttime.isoformat()
  response_dict['start_time'] = starttime
  response_dict['message'] = "Recording set"
else:
  response_dict['status'] = False
  response_dict['message'] = "Sorry, couldn't find a matching programme"

#print response_dict
print json.dumps(response_dict) #, ensure_acsii=False)
