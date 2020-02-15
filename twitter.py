import tweepy
import yaml

with open('config.yml', 'r') as cfgfile:
    config = yaml.load(cfgfile, Loader=yaml.FullLoader)
consumer_token = config['tokens']['twitter']['consumer_token']
consumer_secret = config['tokens']['twitter']['consumer_secret']
access_token = config['tokens']['twitter']['access_token']
access_secret = config['tokens']['twitter']['access_secret']

def tweet(msg):
	auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
	auth.set_access_token(access_token, access_secret)
	api = tweepy.API(auth)

	try:
		api.update_status(msg)
		return "> Successfully posted status to twitter."
	except tweepy.TweepError:
		return "> Error while posting status to twitter."
