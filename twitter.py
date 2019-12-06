import tweepy

with open("tokens.txt", "r") as tokens_file:
	for line in tokens_file:
		if line.startswith("consumer_token: "):
			consumer_token = line.split(": ")[1]
		elif line.startswith("consumer_secret: "):
			consumer_secret = line.split(": ")[1]
		elif line.startswith("access_token: "):
			access_token = line.split(": ")[1]
		elif line.startswith("access_secret: "):
			access_secret = line.split(": ")[1]

def tweet(msg):
	auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
	auth.set_access_token(access_token, access_secret)
	api = tweepy.API(auth)

	try:
		api.update_status(msg)
		return "> Status posted to twitter."
	except tweepy.TweepError:
	    return "> Failed to post status to twitter: "+TweepError.response.text
