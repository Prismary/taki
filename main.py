import discord
import asyncio
import random
import datetime
import os
import time
import twitter as t

with open("tokens.txt", "r") as tokens_file:
	for line in tokens_file:
		if line.startswith("discord_token: "):
			discord_token = line.split(": ")[1].replace("\n","")

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

def load():
	print(pf("i")+"Loading data...")
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
	i_c = 0
	i = 0

	print(pf("i")+"Data loaded.")

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
			t.tweet("I will be inaccessible for a while. Sorry!")
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
			t.tweet(message.content[7:])
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
	print(pf("DONE")+"Taki ready!\n")

print(pf("(o/)")+"Taki starting up!")

print(pf("i")+"Initializing...")
admins = []
auth = []
whitelist = True
print(pf("i")+"> Lists initialized.")
print(pf("i")+"Initialized.")
load()
print(pf("i")+"Logging into discord...")
client.run(discord_token)
