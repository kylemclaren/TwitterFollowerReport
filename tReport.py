#  Many thanks to "tweepy" library.     |
#  https://github.com/tweepy/tweepy     |
#  -------------------------------------
#  Implemented by Onur BAYSAN |
#  onurbaysan@outlook.com     |
#  ---------------------------

import tweepy
import webbrowser
import time
import logging
import sys
import json
import os
import smtplib
from email.mime.text import MIMEText

## Mail Settings
me = [YOUR_MAIL_ADDRESS]
mail_password = [MAIL_PASSWORD]
you = [TO_MAIL_ADDRESS]

# Storage file for access key and access secret
filename = 'setting.txt'

# Daily followers list 
followers_list_file = 'followers.txt'

## Change consumer_key and consumer_secret with your own values
consumer_key=[CONSUMER_KEY]
consumer_secret=[CONSUMER_SECRET]

# List for the users to be followed
followers = []
last_followers = []
tokens = {}

def main():		
	api = authorize()
	
	if loadFollowers() is False:
		saveFollowers(api)
	
	checkFollowers(api)	
	
def searchForTokens(filename):
	try:
	   with open(filename) as f: pass
	except IOError as e:
	   return False
	   
	file = open(filename , 'r')
	str = file.read()
	decoded_str = json.loads(str)		
	tokens['key'] = decoded_str['key']
	tokens['secret'] = decoded_str['secret']
	file.close()	
	return True

def authorize():
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	
	isExist = searchForTokens(filename)
	
	if isExist is False:	
		# Open authorization URL in browser
		webbrowser.open(auth.get_authorization_url())

		# Ask user for verifier pin
		pin = raw_input('Enter the verification pin number from twitter.com: ').strip()

		try: 
			# Get access token
			token = auth.get_access_token(verifier=pin)
			auth.set_access_token(token.key, token.secret)
			api = tweepy.API(auth)
			api.me().name
			tokens['key'] = token.key
			tokens['secret'] = token.secret
			encoded_str = json.dumps(tokens)				
			# Store access key and access secret 			
			file = open(filename , 'w')
			file.write(encoded_str)
			file.close()		
		except Exception, e:
			logging.error(e)
			sys.exit(0)
	else:
		try: 
			auth.set_access_token(tokens['key'], tokens['secret'])
			api = tweepy.API(auth)	
			api.me().name
		except Exception, e:
			#Stored access key and secret are not valid. Delete storage
			os.remove(filename)			
			logging.error(e)
			sys.exit(0)	
	
	return api
	
def loadFollowers():
	try:
	   with open(followers_list_file,'r') as f: pass
	except IOError as e:
	   return False
	   
	full_text = open(followers_list_file,'r')
	for line in full_text:
		last_followers.append(line.strip())
	
	return True
	
def saveFollowers(api):
	for users in tweepy.Cursor(api.followers).items():
		followers.append(users.screen_name)
	
	file = open(followers_list_file , 'w')
	file.write('\n'.join(followers))
	file.close()				
	
def checkFollowers(api):
	for users in tweepy.Cursor(api.followers).items():
		followers.append(users.screen_name)
	
	ff = set(followers).difference(set(last_followers))
	newfollowers = list(ff)
	unfollowers = list(set(last_followers).difference(set(followers)))	
	reportAsMail(newfollowers, unfollowers)

def reportAsMail(newfollowers , unfollowers):
	pure_msg = '------------------\nNew Followers: ' + '\n------------------\n' + '\n'.join(newfollowers) + '\n------------------\n'
	pure_msg = pure_msg + 'Unfollowers: ' + '\n------------------\n' + '\n'.join(unfollowers) 
	msg = MIMEText(pure_msg)
	
	msg['Subject'] = 'Daily followers report, follower_report'
	msg['From'] = me
	msg['To'] = you

	sender = smtplib.SMTP("smtp.gmail.com" , 587)
	sender.ehlo()
	sender.starttls()
	sender.ehlo()
	sender.login(me, mail_password)
	sender.sendmail(me, [you], msg.as_string())
	sender.quit()
		
	print 'Report was sent you successfully. Check your mailbox.'
		
if __name__ == "__main__":
    main()
