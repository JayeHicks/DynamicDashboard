"""
Jaye Hicks

Obligatory legal disclaimer:
 You are free to use this source code (this file and all other files 
 referenced in this file) "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER 
 EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE 
 ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THIS SOURCE CODE IS WITH 
 YOU.  SHOULD THE SOURCE CODE PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL 
 NECESSARY SERVICING, REPAIR OR CORRECTION. See the GNU GENERAL PUBLIC 
 LICENSE Version 3, 29 June 2007 for more details. 
 
This module contains Python code designed to be an AWS Lambda funciton invoked
by an end user call to an AWS API Gateway endpoint.  The user call supplies 
a query string parameter that is in turn made available to this function
via a list named 'event'.  This function's purpose is to access a public 
endpoint, extract data, and return live music performance information. 
"""
import urllib.request
import json
from datetime import datetime, date, timedelta

def lambda_handler(event, context):
  """
  Extract JSON from http://sherlockspub.com/addison/events that contains
  live music calendar information

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
  TARGET_URL = 'http://sherlockspub.com/addison/events'
  START_TAG = '"weeks":'  #index to start of JSON string
  schedule = []
  
  if(event['dayId'].lower() == 'wed'):
    DAY_INPUT_STR  = 'Wed'
    DAY_INPUT_CODE = 2
  elif(event['dayId'].lower() == 'fri'):
    DAY_INPUT_STR  = 'Fri'
    DAY_INPUT_CODE = 4
  else:                       # default setting
    DAY_INPUT_STR  = 'Sat'
    DAY_INPUT_CODE = 5
  
  try:
    with urllib.request.urlopen(TARGET_URL) as response:
      RAW_HTML_BYTES = response.read()
  except Exception as e:
    RAW_HTML_STRING = ''
  else:
    RAW_HTML_STRING = RAW_HTML_BYTES.decode()
  
  if(RAW_HTML_STRING):  
    json_location = RAW_HTML_STRING.find(START_TAG, 0)
    if(json_location != -1):
      json_location += len(START_TAG)
      event_list = extract_list(RAW_HTML_STRING, json_location)
      
      if(event_list):
        for a_week in event_list:
          for a_day in a_week['days']:
            date_string = a_day.get('datetime','')
            if(date_string >= CURRENT_DATE_STR):
              date_object = date(int(date_string[0:4]), 
                                 int(date_string[5:7]), 
                                 int(date_string[8:10]))
              if(date_object.weekday() == DAY_INPUT_CODE):
                event = a_day.get('hasEvent', '')
                if(event):
                  if(event['type'] == 'Music'):
                    band = event['post_name']
                    band = band.replace('-', ' ')
                    band = band.title()
                    display_date = (DAY_INPUT_STR + '   ' + date_string[5:7]
                                    + '.' + date_string[8:10])
                    schedule.append({'date' : display_date, 'band' : band})          
  return(schedule)
      
def extract_list(string, index):
  """
  Extract a list from an JSON input string.
  
  Args:
    string : arbitrary string containing a JSON list
    index : position in string of the JSON list's opening '[' 

  Returns:
    Python list matching the JSON list contained in the input string.  An
    Emtpy list will be returned if bad parameters or processing error occured
  """
  target_string = ''
  list = []
 
  if((string) and (index > 0) and (index < len(string))):
    if(string[index] == '['):
      left = 1
      right = 0
      target_string += string[index]
      index += 1
      
      while((index < len(string)) and (left > right)):
        if(string[index] == '['):
          left += 1
        elif(string[index] == ']'):
          right += 1
        target_string += string[index]
        index += 1
      try:
        list = json.loads(target_string)
      except Exception as e:
        list = []
  return(list)
    
