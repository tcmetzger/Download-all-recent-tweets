# Download all recent tweets
 Download up to 3.200 (API limit) most recent tweets from any given username through Twitter API. Supports 240 character tweets.

## Install
Run `pipenv install`.

Then generate API tokens (instruction: https://developer.twitter.com/en/docs/basics/getting-started - this might require applying for a Twitter developer account and creating a developer app). 

Create the following environment variables with you API tokens:
`CONSUMER_KEY = '[CONSUMER_KEY goes here]'`
`CONSUMER_SECRET = '[CONSUMER_SECRET goes here]'`
`ACCESS_TOKEN = '[ACCESS_TOKEN goes here]'`
`ACCESS_SECRET = '[ACCESS_SECRET goes here]'`

## Run
The username is supplied via the command line argument --screen_name. For example: 
`main.py --screen_name yourscreenname`
