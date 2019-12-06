# Mitsuha AI Project
# Development started on July 7th, 2019

import discord
import asyncio
import random
import datetime
import os
import time
from nltk.tokenize import sent_tokenize, word_tokenize, WordPunctTokenizer
from nltk.stem import WordNetLemmatizer
import twitter

with open("tokens.txt", "r") as tokens_file:
	for line in tokens_file:
		if line.startswith("discord_token: "):
			discord_token = line.split(": ")[1]

client = discord.Client()

def pf(preftype):
	currenttime = str(datetime.datetime.now())[11:19]
	if preftype == "rt":
		return currenttime
	elif preftype == "t" or preftype == "":
		return "["+currenttime+"] "
	elif preftype == "i":
		return "["+currenttime+"/Info] "
	elif preftype == "e":
		return "["+currenttime+"/ERROR] "
	else:
		return "["+currenttime+"/"+preftype+"] "

def coinflip():
	if random.randrange(0,2) == 0:
		return "Heads"
	else:
		return "Tails"

def status(message):
	if enable_twitter == True:
		print(pf("Twitter")+twitter.tweet(message))

def load():
	print(pf("i")+"Loading data...")
	words.clear()
	phrases.clear()
	users.clear()
	admins.clear()

	i_c = 0
	i = 0
	with open("data/admins.txt", "r") as admins_file:
		for line in admins_file:
			admins.append(line.replace("\n", ""))
			i += 1
	print(pf("i")+"> Loaded "+str(i)+" admins.")
	i = 0

	with open("data/whitelist.txt", "r") as whitelistfile:
		for line in whitelistfile:
			auth.append(line.replace("\n", ""))
			i += 1
	print(pf("i")+"> Loaded "+str(i)+" authorized users.")
	i = 0

	for folder in os.listdir("data/words"):
		i_c += 1
		words[folder] = {}

		with open("data/words/"+folder+"/nouns.txt", "r") as nounlist:
			words[folder]["n"] = []
			for line in nounlist:
				words[folder]["n"].append(line.replace("\n", ""))
				i += 1

		with open("data/words/"+folder+"/verbs.txt", "r") as verblist:
			words[folder]["v"] = []
			for line in verblist:
				words[folder]["v"].append(line.replace("\n", ""))
				i += 1

		with open("data/words/"+folder+"/keywords.txt", "r") as keywordlist:
			words[folder]["k"] = []
			for line in keywordlist:
				words[folder]["k"].append(line.replace("\n", ""))
				i += 1


	print(pf("i")+"> Loaded "+str(i)+" words from "+str(i_c)+" categories.")
	i_c = 0
	i = 0

	for file in os.listdir("data/phrases"):
		i_c += 1
		phrases[file] = {}
		with open("data/phrases/"+file+".txt", "r") as phraselist:
			words[file] = []
			for line in phraselist:
				words[file].append(line.replace("\n", ""))
				i += 1
	print(pf("i")+"> Loaded "+str(i)+" phrases from "+str(i_c)+" categories.")
	i_c = 0
	i = 0

	for file in os.listdir("data/users"):
		i_c += 1
		users[file.replace(".txt", "")] = {}
		with open("data/users/"+file, "r") as userfile:
			users[file.replace(".txt", "")]["username"] = userfile.readline().replace("\n", "")
			i += 1
	print(pf("i")+"> Loaded "+str(i)+" users.")
	i_c = 0
	i = 0

	print(pf("i")+"Data loaded.")

def save_word(word, wordtype, category):
	with open("data/words/"+category+"/"+wordtype+".txt", "a") as wordfile:
		wordfile.write(word+"\n")

def save_user(userid, username):
	with open("data/users/"+userid+".txt", "w") as userfile:
		userfile.write("username: "+users[userid]["username"])

def check_category(category):
	if not category in words:
		words[category] = {"n":[],"v":[],"k":[]}
		os.mkdir("data/words/"+category)
		mkfile = open("data/words/"+category+"/nouns.txt", "x")
		mkfile.close()
		mkfile = open("data/words/"+category+"/verbs.txt", "x")
		mkfile.close()
		mkfile = open("data/words/"+category+"/keywords.txt", "x")
		mkfile.close()
		status("I just learned about "+category+"!")

def check_user(userid, username):
	if not userid in users:
		users[userid] = {"username":username}
		save_user(userid, username)

def ai(message):
	if message.content.lower().split(" ")[1] == "keyword":
		category = message.content.lower().split(" ")[0]
		keyword = message.content.lower().split(" ")[2]
		check_category(category)
		if not keyword in words[category]["k"]:
			words[category]["k"].append(keyword)
			save_word(keyword, "keywords", category)

		return "Thanks, I'll do my best to remember this!"

	else:
		category = message.content.lower().split(" ")[0]
		check_category(category)

		word_tokens = word_tokenize(message.content.lower().replace("\n","").replace(".","").replace(",","").replace("!","").replace("?","").replace("\"","").replace("\'","").replace(":","").replace("- ",""))
		for word in word_tokens:
			noun = lemmatizer.lemmatize(word, pos='n')
			verb = lemmatizer.lemmatize(word, pos='v')
			if not noun in words[category]["n"] and not noun in words["general"]["n"]:
				words[category]["n"].append(noun)
				save_word(noun, "nouns", category)
			if not verb in words[category]["v"] and not verb in words["general"]["v"]:
				words[category]["v"].append(verb)
				save_word(verb, "verbs", category)

		return "Thank you for telling me about "+message.content.split(" ")[0]+"!"

@client.event
async def on_message(message):
	channel = message.channel
	print(pf("")+str(message.author)+": "+message.content)
	if message.author == client.user:
		return
	global whitelist
	if whitelist == True and not str(message.author) in auth:
		await channel.send("Sorry, I may only talk to authorized users.")
		return

	check_user(str(message.author.id), str(message.author))

	if message.content.startswith(".") and str(message.author) in admins:
		if message.content.lower().split(" ")[0] == ".stop":
			await channel.send("`"+pf("i")+"Client logout called."+"`")
			status("I will be inaccessible for a while. Sorry!")
			await client.logout()
		elif message.content.lower().split(" ")[0] == ".ping":
			await channel.send("`"+pf("i")+"Pong!"+"`")
		elif message.content.lower().split(" ")[0] == ".i":
			print(pf("i")+"Message ignored.")
		elif message.content.lower().split(" ")[0] == ".api":
			await channel.send("`"+pf("i")+discord.__version__+"`")
		elif message.content.lower().split(" ")[0] == ".reload":
			load()
			await channel.send("`"+pf("i")+"Data successfully reloaded."+"`")
		elif message.content.lower().split(" ")[0] == ".coinflip":
			await channel.send("`"+pf("Coinflip")+"Result: "+coinflip()+"`")
		elif message.content.lower().split(" ")[0] == ".twitter":
			if message.content.lower().split(" ")[1] == "on":
				enable_twitter = True
				await channel.send("`"+pf("i")+"Twitter successfully enabled."+"`")
			elif message.content.lower().split(" ")[1] == "off":
				enable_twitter = False
				await channel.send("`"+pf("i")+"Twitter successfully disabled."+"`")
			else:
				await channel.send("`"+pf("i")+"enable_twitter = "+str(enable_twitter)+"`")
		elif message.content.lower().split(" ")[0] == ".tweet":
			twitter.tweet(message.content[7:])
			await channel.send("`"+pf("Tweet")+"Twitter status update called."+"`")
		elif message.content.lower().split(" ")[0] == ".whitelist":
			if message.content.lower().split(" ")[1] == "on":
				whitelist = True
				await channel.send("`"+pf("i")+"Whitelist successfully enabled."+"`")
			elif message.content.lower().split(" ")[1] == "off":
				whitelist = False
				await channel.send("`"+pf("i")+"Whitelist successfully disabled."+"`")
			else:
				await channel.send("`"+pf("i")+"auth = "+str(auth)+"`")
		else:
			await channel.send("`"+pf("e")+"Invalid command."+"`")

	elif message.content.lower() == "hello!":
		await channel.send("Hi there!")
	elif message.content.lower() == "flip a coin!":
		await channel.send("Sure, just a second.")
		time.sleep(random.randrange(1, 4))
		await channel.send("It landed "+coinflip()+"!")

	else:
		await channel.send(ai(message))

@client.event
async def on_ready():
	print(pf("i")+"> Username: "+client.user.name+"\n"+pf("i")+"> User-ID: "+str(client.user.id))
	status("I'm back online!")
	print(pf("DONE")+"Mitsuha ready!\n")

print(pf("(o/)")+"Mitsuha starting up! ^-^/")

print(pf("i")+"Initializing...")
lemmatizer = WordNetLemmatizer()
print(pf("i")+"> Lemmatizer defined.")
words = {}
phrases = {}
users = {}
admins = []
auth = []
whitelist = True
enable_twitter = True
print(pf("i")+"> Lists initialized.")
print(pf("i")+"Initialized.")
load()
print(pf("i")+"Logging into discord...")
client.run(discord_token)
