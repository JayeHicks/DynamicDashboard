# Dynamic Dashboard
This repository does not contain a bundle of source code that you can simply clone to your machine and bring up a functioning managerial decision support dashboard.  While it does contain some source code and technical guidance, it is intended to serve as a template that you can use to create a solution similar to one that I delivered to a client in need of a decision support dashboard that dynamically sourced up-to-date information.

## Context for Dynamic Dashboard Development
My client was a regional director, in the civil construction business unit, of an international heavy construction company.  Delivery on contracts awarded to his company required intense coordination of not only internal activities but also coordination of external activities and of information (e.g., subcontractors, vendors, suppliers, client).   Upon reaching the limits of his centralized, internal IT department, my client sought my advice.  I developed and demonstrated a Proof of Concept (POC), secured approval to move forward with solution development, and ultimately delivered a fully operational dynamic, decision support dashboard.  Solution development involved working with my client’s local IT staff as well as several entities external to my client’s organization (e.g., subcontractors, vendors, suppliers, client).  After reviewing the results of using the solution on a single project, my client directed his local IT staff to deploy the solution on all high-risk and / or complex projects under his span of control.  While there is some potential for corporate-wide adoption of the solution, the introduction and subsequent adoption of bottom-up IT initiatives is typically an uphill struggle in established, traditional organizations that have centralized IT departments.  Resistance to change, regardless of the merits of said change, often proves to be insurmountable. :)

![Image1](doco-images/ConceptArchXSmall.jpg)

For obvious reasons, the source code snippets provided in this repository came from the POC; not from the production solution delivered to my client.  However, the POC is feature complete, containing all of the functionality that I ultimately delivered to my client.  It is AWS-based and 100% severless. 

## Solution Components
* Single-Page Web Application
* Backend

NOTE: 
While I do provide source code snippets and technical guidance for implementing this solution, I do not provide background explanations of AWS services.  Simple Internet searches can easily provide this information.  The target audience for this repository is experienced AWS solution architects.


### Single-Page Web Application
#### Application Overview
The twelve files located in https://github.com/JayeHicks/DynamicDashboard/tree/master/web-app
 constitute  the POC’s single-page web application.  All 12 files are hosted in an S3 bucket configured for static web hosting.  

A quick study of the index.html will reveal that html button pushes result in invoking AWS-hosted Internet accessible endpoints.  Invoking such an endpoint (i.e., AWS API Gateway API) results in the execution of an AWS Lambda function.  The Lambda functions in turn access an Internet accessible endpoint, retrieve data of interest, format the data, and return the formatted data to the end user’s web browser.  More information on the Lambda functions is provided below in the “Data Acquisition” section.   This will serve as a simplified application architecture diagram.

 ![Image1](doco-images/HLAppArch.jpg)

NOTE:
The eleven JavaScript files were generated using the API Gateway portion of the AWS Console. To generate these files select an API Gateway API, select “Stages”, select “prod”, select “SDK Generation”, use the drop down selection box to select a platform (e.g., JavaScript), and select “Generate SDK.”  Ten of the eleven files will be identical regardless of which API you decide to use when generating the eleven files.  I modified the unique file, apigClient.js, so that a single set of eleven JavaScript files can facilitate any number of AWS API Gateway APIs.  In order for this modified JavaScript file to work for you, you will need to set an attribute in your single page web application (e.g., index.html).

#### Security
The POC single page web application requires both authentication and authorization before an end user can gain access to any application functionality. 
  
Authentication is achieved through Web Identity Federation with Facebook.  In the file index.html you can see the JavaScript functions enabling this federation.  In addition to adding the Facebook federation JavaScript to your single page web application, two preliminary actions are required.  First, you must access the Facebook app development website in order to set up a Facebook app and thereby obtain a Facebook app id.  Second, you must create and configure an AWS Cognito User Identity Pool that trusts users who are successfully logged into Facebook.  While configuring the User Identity Pool, in “Authentication Providers” select the “Facebook” tab so that you can enter the Facebook App ID that was obtained in step one.  Creating a User Identity Pool results in the automatic creation of two IAM roles.  Even though authorization will be handled by Lambda Authorizers on each individual API Gateway endpoint, ensure that you do not delete or reduce permission level on either of these IAM roles.   

In the POC single page web application’s initial default state, the push button controls necessary to invoke the functionality behind the API Gateway endpoints are inactive.  When any end user is properly authenticated via Facebook the state of these push button controls changes to active.  However, while anyone who authenticated via Facebook can click these push button controls, only a limited number of named individuals can successfully invoke the functionality behind the API Gateway endpoints.

The permission to successfully invoke API Gateway endpoints is granted by a Lambda Authorizer function.  It decides whether or not the POC single page web application’s end user will be allowed to invoke a given API.  This decision is based on the end user’s Facebook User ID.  In the original request from the end user’s browser for an API Gateway endpoint, the end user’s Facebook User ID is passed along as a query string parameter.  Study of index.html will reveal that the Facebook User ID of web application’s end user is captured after successful authentication with Facebook.  For the POC, I elected to use a Request Lambda Authorizers vs a Token Lambda Authorizer.  A single Request Lambda Authorizer is used to secure all of the API Gateway APIs.  In this fashion the POC employs a “white listing” strategy to grant access to the web application’s functions to a select number of named individuals whose Facebook User Ids are maintained in the Lambda Authorizer’s source code.

To set up Lambda Authorizers for your API Gateway APIs first create your Lambda Authorizer function.  Then, for each API, in the API Gateway section of the AWS Console select “Authorizers”, select “Create New Authorizer”, and fill out the required information which involves selecting the Lambda Authorizer that you previously created.  When modifying API Gateway APIs don’t forget to promote your changes to ‘prod.’ 

Here is a genericized template that you can use to get started building your Lambda Authorizer.  In this template a request is “authorized” only if the client-supplied HeaderAuth1 header, QueryString1 query parameter, stage variable of StageVar1, and the accountId in the request context all match the specified values of 'headerValue1', 'queryValue1', 'stageValue1', and '123456789012', respectively.  While this example demonstrates three different mechanisms, for authorization in the POC I only used a single query string parameter.

```
import re

#Facebook user ids
authorizedUsers = ['123456789012345678']

def lambda_handler(event, context):
  """
  This module is an AWS Lambda function that serves as a Lambda
  Authorizer of type Request.  It is used to arbitrate access to
  multiple API Gateway endpoints that are accessible via the Live 
  Music Calendar web application.  The web application logs an 
  end user into Facebook, for authentication, and captures the 
  user's Facebook user id in the process. This function authorizes
  or denies to the AWS API Gateway endpoints by determining whether 
  or not the captured Facebook user id is in a static, short list of
  user ids that is maintained inside of the Authorizer itself.
  """
  tmp = event['methodArn'].split(':')
  apiGatewayArnTmp = tmp[5].split('/')
  awsAccountId = tmp[4]
  principalId = event['queryStringParameters']['fbUserId']
  policy = AuthPolicy(principalId, awsAccountId)
  policy.restApiId = apiGatewayArnTmp[0]
  policy.region = tmp[3]
  policy.stage = apiGatewayArnTmp[1]
  if(principalId in authorizedUsers):
    policy.allowMethod(HttpVerb.GET, '*')
    policy.allowMethod(HttpVerb.OPTIONS, '*')
  else:
    policy.denyAllMethods()

  authResponse = policy.build()
  
  return(authResponse)


class HttpVerb:
  GET     = 'GET'
  POST    = 'POST'
  PUT     = 'PUT'
  PATCH   = 'PATCH'
  HEAD    = 'HEAD'
  DELETE  = 'DELETE'
  OPTIONS = 'OPTIONS'
  ALL     = '*'


class AuthPolicy(object):
  """
  Internal lists of objects representing allowed and denied methods.
  Each object has 2 properties: a resource ARN and a conditions 
  statement (which can be null). The build method processes these 
  lists to generate the final policy.

  """
  awsAccountId = ''
  principalId = ''           # email of user attempting to invoke API
  version = '2012-10-17'
  pathRegex = '^[/.a-zA-Z0-9-\*]+$'   # pattern for valid resource paths 

  allowMethods = []
  denyMethods = []

  restApiId = '*'
  region = '*'
  stage = '*'

  def __init__(self, principal, awsAccountId):
    self.awsAccountId = awsAccountId
    self.principalId = principal
    self.allowMethods = []
    self.denyMethods = []

  def _addMethod(self, effect, verb, resource, conditions):
    """
    The condition statement can be null.
    """
    if((verb != '*') and (not hasattr(HttpVerb, verb))):
      raise NameError('Invalid HTTP verb ' + verb + 
                      '. Allowed verbs in HttpVerb class')
    resourcePattern = re.compile(self.pathRegex)
    if(not resourcePattern.match(resource)):
      raise NameError('Invalid resource path: ' + resource + 
                      '. Path should match ' + self.pathRegex)

    if(resource[:1] == '/'):
      resource = resource[1:]

    resourceArn = 'arn:aws:execute-api:{}:{}:{}/{}/{}/{}'.format(
                                                            self.region, 
                                                            self.awsAccountId, 
                                                            self.restApiId, 
                                                            self.stage, verb, 
                                                            resource)
    if(effect.lower() == 'allow'):
      self.allowMethods.append({'resourceArn': resourceArn,
                                'conditions': conditions})
    elif(effect.lower() == 'deny'):
      self.denyMethods.append({'resourceArn': resourceArn,
                               'conditions': conditions})


  def _getEmptyStatement(self, effect):
    """
    Returns an empty statement object prepopulated with the correct 
    action and the desired effect.
    """
    statement = {'Action': 'execute-api:Invoke',
                 'Effect': effect[:1].upper() + effect[1:].lower(),
                 'Resource': []}
    return(statement)

  def _getStatementForEffect(self, effect, methods):
    """
    Loops over an array of objects (each containing a resourceArn and 
    conditions statement [which may be null]) and generates an array of 
    individual statements for the policy.
    """
    statements = []

    if(len(methods) > 0):
      statement = self._getEmptyStatement(effect)

      for curMethod in methods:
        if((curMethod['conditions'] is None) or 
           (len(curMethod['conditions']) == 0)):
          statement['Resource'].append(curMethod['resourceArn'])
        else:
          conditionalStatement = self._getEmptyStatement(effect)
          conditionalStatement['Resource'].append(curMethod['resourceArn'])
          conditionalStatement['Condition'] = curMethod['conditions']
          statements.append(conditionalStatement)

      if(statement['Resource']):
        statements.append(statement)

    return(statements)

  def allowAllMethods(self):
    self._addMethod('Allow', HttpVerb.ALL, '*', [])

  def denyAllMethods(self):
    self._addMethod('Deny', HttpVerb.ALL, '*', [])

  def allowMethod(self, verb, resource):
    self._addMethod('Allow', verb, resource, [])

  def denyMethod(self, verb, resource):
    self._addMethod('Deny', verb, resource, [])

  def allowMethodWithConditions(self, verb, resource, conditions):
    self._addMethod('Allow', verb, resource, conditions)

  def denyMethodWithConditions(self, verb, resource, conditions):
    self._addMethod('Deny', verb, resource, conditions)

  def build(self):
    """
    Generates the policy document based on the lists of allowed and 
    denied conditions. Generates a policy with two main statements for
    the effect: one for Allow and one statement for Deny.  Methods that 
    include conditions will have their own statement in the policy.
    """
    if(((self.allowMethods is None) or (len(self.allowMethods) == 0)) and
       ((self.denyMethods is None) or (len(self.denyMethods) == 0))):
      raise NameError('No statements defined for the policy')

    policy = {'principalId': self.principalId,
              'policyDocument': {'Version': self.version,
                                 'Statement': []}}

    policy['policyDocument']['Statement'].extend(
      self._getStatementForEffect('Allow', self.allowMethods))
    policy['policyDocument']['Statement'].extend(
      self._getStatementForEffect('Deny', self.denyMethods))

    return(policy)
```

An application architecture diagram depicting the flow of execution (starting with end user log on through to successful access of application functionality) is presented below, but broken up into two diagrams.  A single diagram would have involved an overwhelming amount of detail.  The first diagram illustrates the general flow from end user logon through to attempting to invoke application functionality.  Authorization is required to invoke the application’s functionality and this authorization flow is depicted in the second diagram.  If you want to conceptually integrate the two diagrams, step 8 from the first diagram roughly translates picks up in step 4 of the second diagram. 


High Level Flow (without detail of Lambda Authorizers)
![Image1](doco-images/AppArchFlow1.jpg)




High Level Flow of Lambda Authorizers
![Image1](doco-images/AppArchFlow2.jpg)

### Backend
#### Overview
I designed the POC such that a single API Gateway API is dedicated to acquiring a particular type of information (i.e., live music performance schedule for a given venue).  There is a one-to-one relationship between API Gateway APIs and data collection Lambda functions.  Two query string parameters are passed to an API Gateway API, and subsequently a Lambda function, each time the end user makes a request via the single page web application.  One query string parameter is used by the Lambda Request Authorizer (i.e., Facebook User ID) and the other is used inside of the data collection Lambda function to refine the collected information before it is presented back to the end user (i.e., a venue’s live music performance schedule for a given day of the week).  

Creating API Gateway APIs that invoke Lambda functions is fairly straightforward as is creating Lambda functions that are triggered by API Gateway APIs.  A considerable amount of on-line documentation exists to help you with either task.
 
#### Data Acquisition
For the POC, I wrote python scripts that access Internet accessible endpoints, retrieve information, format the information, and return the formatted information back to the end user.  You can see the scripts used in the POC, and still in use today, at https://github.com/JayeHicks/DynamicDashboard/tree/master/data-collection.  At this time, one of the original endpoints (i.e., in use since 2018) has changed format and I have yet to decide whether or not to employ a headless browser in order to secure the desired information.  While I would enjoy the challenge, it really just comes down to finding the free time. 

#### Security
The data collection Lambda functions can only be invoked by the API Gateway APIs.  Lambda Authorizers determine which single page web application end users can invoke an API Gateway API.  I kept things simple in the POC; a white list of Facebook User IDs is maintained in the Lambda Authorizer.

## Final Thoughts
Web Identity Federation with Facebook frees you from having to manage user ids and passwords, but it does come at a price.  With the initial deployment of the POC, Facebook allowed my Facebook App to have an “http” URL.  This changed over time and I was forced into changing to an “https” URL for my web application.  Since I wanted to continue hosting my application in an S3 bucket configured for static web hosting, I wound up creating an AWS CloudFront distribution for my web application that did nothing more than provide an “https” URL (i.e., offload https traffic and route http traffic to my S3 bucket).  While this took all of 5 minutes, its annoying to mess with something that is already working and to have to add another technical component to a solution; not to mention having to roll out a new URL to all of my friends who have become addicted to my Live Music Calendar application.  Additionally, be aware that Facebook monitors all of its registered Facebook Apps.  My guess is that they do not want name brand association with applications that would reflect poorly upon them (e.g., non functioning applications or applications with broken links).  I suspect that Facebook employs bots to crawl all of their registered Facebook Apps in order to catch certain issues and send out automated emails.  When one of the Internet accessible endpoints that my POC was scraping changed formats,  I got an automated email from Facebook.  Out of curiosity, I responded to the email and from that point forward I began trading email with an actual human.  It turned out to be different people for each response but the responses were definitely from humans.  The fix was easy, but it is worth noting that Facebook will expend time and energy keeping tabs on your application if you use Facebook Web Identity Federation.  

## License
This project is licensed under the GNU Public License v3.0.  For details see: https://github.com/JayeHicks/DynamicDashboard/blob/master/LICENSE
