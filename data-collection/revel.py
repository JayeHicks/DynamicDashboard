"""
This module contains Python code designed to be an AWS Lambda funciton invoked
by an end user call to an AWS API Gateway endpoint.  The user call supplies 
a query string parameter that is in turn made available to this function
via a list named 'event'.  This function's purpose is to access a public 
endpoint, extract data, and return live music performance information. 
"""
import json
import urllib.request
from datetime import datetime, date, timedelta

def lambda_handler(event, context):
  """
  Processing:
    The following endpoint
      "https://www.googleapis.com/calendar/v3/calendars/" +
      "reservoirfrisco@gmail.com/" +
      "events?key=AIzaSyCNpHo-Y0zKpgBHHj4Pnv1TGWZQFcd62e4" +
      "&maxResults=5000"
    returns a JSON object containing a list of JSON objects, each 
    list item representing an individual live music performance.  Cycle
    through list items to build a list of the relevent performances.
    
    Future issue:
    The endpoint is a Google calendar that continus to grow.  At some
    point in the future a single call to the endpoint will not return all
    of the information contained in the calendar.  When this happens the
    JSON object returned will contain a key named 'nextPageToken.'  To 
    access the next page of data (i.e., another JSON object), make the 
    same call again but add to it a query string parameter 
    "&nextPageToken=...".  The value to set this parameter is displayed 
    in the first page (i.e., JSON object)    

  Args:
    event: passed by the Lambda service and contains query string parms
      {'dayId' : <value>} is passed in by the Lambda service
    context: passed by AWS Lambda

  Returns:
    List of dictionaries each dictionary representing a single live
    performance or empty list if no events exist of if an error
    occured.  Example output:
    
    [{'date': 'Fri 10.04', 'band': 'Mullet Boyz'}, {'date': 
    'Fri 10.11', 'band': 'Electric Circus'}, {'date': 'Fri 10.18', 
    'band': 'Vegas Stars'}, {'date': 'Fri 10.25', 'band': 'Overdrive'}]   
  """
  #US Central Time zone == UTC - 6 hours; will need to filter out past events
  CURRENT_DATE_TIME = datetime.utcnow() - timedelta(hours = 6)
  CURRENT_DATE_STR = str(CURRENT_DATE_TIME.date())
  TARGET_URL = ''.join(["https://www.googleapis.com/calendar/v3/calendars/",
                        "reservoirfrisco@gmail.com/",
                        "events?key=AIzaSyCNpHo-Y0zKpgBHHj4Pnv1TGWZQFcd62e4",
                        "&maxResults=5000"])
  schedule = []
  
  if(event['dayId'].lower() == 'wed'):
    DAY_INPUT_STR  = 'Wed'
    DAY_INPUT_CODE = 2
  elif(event['dayId'].lower() == 'fri'):
    DAY_INPUT_STR  = 'Fri'
    DAY_INPUT_CODE = 4
  else:                       #default to Saturday
    DAY_INPUT_STR  = 'Sat'
    DAY_INPUT_CODE = 5
  
  try:
    with urllib.request.urlopen(TARGET_URL) as response:
      RAW_LIST = json.loads(response.read())
  except Exception as e:
    RAW_LIST = ''
    
  if(RAW_LIST):
    for event in RAW_LIST["items"]:
      if("date" in event["start"]):
        date_string = event["start"]["date"]
      else:
        date_string = event["start"]["dateTime"][0:10]
      if(date_string >= CURRENT_DATE_STR):
        event_date = date(int(date_string[0:4]),
                          int(date_string[5:7]),
                          int(date_string[8:10]))
        if(event_date.weekday() == DAY_INPUT_CODE):
          date_display = (DAY_INPUT_STR + '   ' + str(event_date.month).zfill(2)
                          + '.' + str(event_date.day).zfill(2))
          schedule.append({'date' : date_display, 'band' : event["summary"]})
    if(schedule):
      schedule = sorted(schedule, key=lambda k: k['date'][4:14])

  return(schedule)
