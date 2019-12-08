import discord
import asyncio
import random
import datetime
import os
import time
import twitter as t
from shutil import copyfile

with open('tokens.txt', 'r') as tokens_file:
	for line in tokens_file:
		if line.startswith('discord_token: '):
			discord_token = line.split(': ')[1].replace('\n','')

client = discord.Client()

def pf(preftype):
	currenttime = str(datetime.datetime.now())[11:19]
	if preftype == 'rt':
		return currenttime
	elif preftype == 't' or preftype == '':
		return '['+currenttime+'] '
	elif preftype == 'i':
		return '['+currenttime+'/Info] '
	elif preftype == 'e':
		return '['+currenttime+'/ERROR] '
	else:
		return '['+currenttime+'/'+preftype+'] '

def load():
	print(pf('i')+'Loading data...')
	admins.clear()
	auth.clear()

	i_c = 0
	i = 0
	with open('data/admins.txt', 'r') as admins_file:
		for line in admins_file:
			admins.append(line.replace('\n', ''))
			i += 1
	print(pf('i')+'> Loaded '+str(i)+' admins.')
	i = 0

	with open('data/whitelist.txt', 'r') as whitelistfile:
		for line in whitelistfile:
			auth.append(line.replace('\n', ''))
			i += 1
	print(pf('i')+'> Loaded '+str(i)+' authorized users.')
	i_c = 0
	i = 0

	print(pf('i')+'Data loaded.')

def process(msg):
	if msg.content == '?':
		return '__**Command-Usage**__\n```Markdown\n# Add a song to the recommendation pool:\n\nadd;<artist>;<title>;<link>\n\n\n# Post a recommendation to Twitter:\n\nrec;[random/;<artist>;<title>]\n```'

	elif msg.content.lower().startswith('add;'):
		try:
			r_artist = msg.content.split(';')[1]
			r_title = msg.content.split(';')[2]
			r_link = msg.content.split(';')[3]
		except:
			return 'The message format is invalid. Type \'?\' for help.'

		with open('data/pending/'+r_artist+'_'+r_title+'.txt', 'w') as r_file:
			r_file.write('artist;'+r_artist+'\n')
			r_file.write('title;'+r_title+'\n')
			r_file.write('link;'+r_link+'\n')

		return 'Successfully added **'+r_artist+' - '+r_title+'** to the recommendation pool.'

	elif msg.content.lower().startswith('rec;'):
		if msg.content.lower().split(';')[1] == 'random':
			for files in os.walk('data/pending'):
				filename = files[2][random.randrange(0, len(files[2])+1)]

			with open('data/pending/'+filename, 'r') as r_file:
				for line in r_file:
					if line.startswith('artist;'):
						r_artist = line.split(';')[1].replace('\n', '')
					elif line.startswith('title;'):
						r_title = line.split(';')[1].replace('\n', '')
					elif line.startswith('link;'):
						r_link = line.split(';')[1].replace('\n', '')
		else:
			try:
				r_artist = msg.content.split(';')[1]
				r_title = msg.content.split(';')[2]
			except:
				return 'The message format is invalid. Type \'?\' for help.'

			try:
				with open('data/pending/'+r_artist+'_'+r_title+'.txt', 'r') as r_file:
					for line in r_file:
						if line.startswith('link;'):
							r_link = line.split(';')[1].replace('\n', '')
			except:
				return 'The specified file does not exist.'

		print(pf('Tweet')+t.tweet(''+r_artist+' - '+r_title+'\n\n'+r_link))
		copyfile('data/pending/'+r_artist+'_'+r_title+'.txt', 'data/posted/'+r_artist+'_'+r_title+'.txt')
		os.remove('data/pending/'+r_artist+'_'+r_title+'.txt')
		print(pf('i')+'> File transferred from /pending/ to /posted/.')
		return 'Successfully posted **'+r_artist+' - '+r_title+'** to Twitter.'

	else:
		return 'Unable to process the message. Type \'?\' for help.'

@client.event
async def on_message(message):
	channel = message.channel
	print(pf('Log')+str(message.author)+': '+message.content)
	if message.author == client.user:
		return
	global whitelist
	if whitelist == True and not str(message.author) in auth:
		await channel.send('Sorry, I may only talk to authorized users.')
		return

	if message.content.startswith('.') and str(message.author) in admins:
		if message.content.lower().split(' ')[0] == '.stop':
			await channel.send('`'+pf('i')+'Client logout called.'+'`')
			await client.logout()
		elif message.content.lower().split(' ')[0] == '.ping':
			await channel.send('`'+pf('i')+'Pong!'+'`')
		elif message.content.lower().split(' ')[0] == '.i':
			print(pf('i')+'Message ignored.')
		elif message.content.lower().split(' ')[0] == '.api':
			await channel.send('`'+pf('i')+discord.__version__+'`')
		elif message.content.lower().split(' ')[0] == '.reload':
			load()
			await channel.send('`'+pf('i')+'Data successfully reloaded.'+'`')
		elif message.content.lower().split(' ')[0] == '.tweet':
			print(pf('Tweet')+t.tweet(message.content[7:]))
			await channel.send('`'+pf('Tweet')+'Twitter status update called.'+'`')
		elif message.content.lower().split(' ')[0] == '.whitelist':
			if message.content.lower().split(' ')[1] == 'on':
				whitelist = True
				await channel.send('`'+pf('i')+'Whitelist successfully enabled.'+'`')
			elif message.content.lower().split(' ')[1] == 'off':
				whitelist = False
				await channel.send('`'+pf('i')+'Whitelist successfully disabled.'+'`')
			else:
				await channel.send('`'+pf('i')+'auth = '+str(auth)+'`')
		else:
			await channel.send('`'+pf('e')+'Invalid command.'+'`')

	elif message.content.lower() == 'hello!':
		await channel.send('Hi there!')

	else:
		await channel.send(process(message))

@client.event
async def on_ready():
	print(pf('i')+'> Username: '+client.user.name+'\n'+pf('i')+'> User-ID: '+str(client.user.id))
	print(pf('DONE')+'Taki ready!\n')

print(pf('(o/)')+'Taki starting up!')

print(pf('i')+'Initializing...')
admins = []
auth = []
whitelist = True
print(pf('i')+'> Lists initialized.')
print(pf('i')+'Initialized.')
load()
print(pf('i')+'Logging into discord...')
client.run(discord_token)
