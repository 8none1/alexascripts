#!/usr/bin/python

import requests
import os
#import sys
import cgi
import json
import logging
import datetime
import datafile


myth_commander_endpoint = datafile.myth_commander_endpoint
ask_app_id = datafile.ask_app_id

ok = False

logging.basicConfig(filename='/tmp/proxy.log', level=logging.DEBUG)
def log(message):
  logging.debug(message)
  #pass

def dispatch_to_commander(title, channel):
  r = requests.post(myth_commander_endpoint, data = {'title':title, 'channel':channel})
  if r.status_code == 200:
    return r.json()
  else:
    return json.dumps({'status':False})


def failed():
  print json.dumps({'status':False})
  ok = False

print "Content-Type: application/json"
print

log("\n\n\nStarting now....")
log(datetime.datetime.now())

if "REQUEST_METHOD" in os.environ.keys() and os.environ['REQUEST_METHOD'] == "POST":
    form = cgi.FieldStorage()
    log(form)
    try:
      title = form["title"].value
      channel = form["channel"].value
      appid = form["appid"].value
      log("Got data from form ok")
      ok = True # This seems necessary because if the script abends or uses sys.exit you get garbage out
    except:
      failed()
      log("Failed trying to decode form data")
      #sys.exit()
elif "REQUEST_METHOD" in os.environ.keys() and os.environ['REQUEST_METHOD'] is not "POST":
    # Unsupported method.
    failed()
    log("Got unsupported method")
else:
  # Here for cli testing only.  Can be removed or commented out later
  title = "Blue Peter"
  channel = "CBBC"
  appid = "amzn1.ask.skill.e0d39143-ebe0-40da-b7fa-babba8eba719"
  ok = True

if ok == True:
  if appid == ask_app_id:
    log("appid passed")
    response_dict = json.dumps(dispatch_to_commander(title, channel))
    log("sending back...")
    log(response_dict)
    print response_dict
  else:
    log("Something bad happened here")

log("Finished now....")
log(datetime.datetime.now())
log("\n\n\n")
