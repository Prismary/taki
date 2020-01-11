import tweepy

with open("tokens.txt", "r") as tokens_file:
	for line in tokens_file:
		if line.startswith("consumer_token: "):
			consumer_token = line.split(": ")[1].replace("\n","")
		elif line.startswith("consumer_secret: "):
			consumer_secret = line.split(": ")[1].replace("\n","")
		elif line.startswith("access_token: "):
			access_token = line.split(": ")[1].replace("\n","")
		elif line.startswith("access_secret: "):
			access_secret = line.split(": ")[1].replace("\n","")

def tweet(msg):
	auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
	auth.set_access_token(access_token, access_secret)
	api = tweepy.API(auth)

	try:
		api.update_status(msg)
		return "> Successfully posted status to twitter."
	except tweepy.TweepError:
		return "> Error while posting status to twitter."
