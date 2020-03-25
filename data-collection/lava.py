"""
This module contains Python code designed to be an AWS Lambda funciton invoked
by an end user call to an AWS API Gateway endpoint.  The user call supplies 
a query string parameter that is in turn made available to this function
via a list named 'event'.  This function's purpose is to access a public 
endpoint, extract data, and return live music performance information. 
"""
import urllib.request
import json
from datetime import date

def lambda_handler(event, context):
  """
  Open page: http://lavacantinathecolony.ticketfly.com/calendar, scrape and 
  return a list of JSON objects representing live music performances.

  Args:
    event: passed by the Lambda service and contains query string parms
      {'dayId' : <value>} is passed in by the Lambda service
    context: passed by AWS Lambda

  Returns:
    List of dictionaries each dictionary representing a single live
    performance or empty list if an error occured. Example output:
    
    [{'date': 'Fri 10.04', 'band': 'Mullet Boyz'}, {'date': 
    'Fri 10.11', 'band': 'Electric Circus'}, {'date': 'Fri 10.18', 
    'band': 'Vegas Stars'}, {'date': 'Fri 10.25', 'band': 'Overdrive'}]   
  """
  TARGET_URL = 'https://lavacantinathecolony.ticketfly.com/'
  START_TAG = '"application/ld+json">'       #index to start of JSON
  schedule = []
  
  if(event['dayId'].lower() == 'wed'):
    DAY_INPUT_STR  = 'Wed'
    DAY_INPUT_CODE = 2
  elif(event['dayId'].lower() == 'fri'):
    DAY_INPUT_STR  = 'Fri'
    DAY_INPUT_CODE = 4
  else:                       #default to Sat
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
        for event in event_list:
          date_string = event["startDate"][0:10]
          date_object = date(int(date_string[0:4]),
                             int(date_string[5:7]), 
                             int(date_string[8:10]))
          if(date_object.weekday() == DAY_INPUT_CODE):
            display_date = (DAY_INPUT_STR + '   ' + date_string[5:7] + '.'
                            + date_string[8:10])
            band = event["name"]
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
