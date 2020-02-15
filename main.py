import discord
import asyncio
import random
import datetime
import os
import time
import sqlite3
import re
import yaml
import twitter as t

conn = sqlite3.connect('taki.db')
conn.create_function('REGEXP', 2, lambda x, y: 1 if re.search(x,y) else 0)
cursor = conn.cursor()

with open('config.yml', 'r') as cfgfile:
    config = yaml.load(cfgfile, Loader=yaml.FullLoader)
whitelist = config['settings']['whitelist']
discord_token = config['tokens']['discord']['discord_token']

client = discord.Client()

def pf(preftype='t'):
	currenttime = str(datetime.datetime.now())[11:19]
	if preftype == 'rt':
		return currenttime
	elif preftype == 't':
		return '['+currenttime+'] '
	elif preftype == 'i':
		return '['+currenttime+'/Info] '
	elif preftype == 'e':
		return '['+currenttime+'/ERROR] '
	else:
		return '['+currenttime+'/'+preftype+'] '

async def send(channel, msg, type='default'):
	if type == 'cmd_i':
		msg = '`'+pf('i')+msg+'`'
	elif type == 'cmd_e':
		msg = '`'+pf('e')+msg+'`'
	elif type == 'cmd_t':
		msg = '`'+pf('t')+msg+'`'
	elif type == 'cmd_tweet':
		msg = '`'+pf('Tweet')+msg+'`'
	await channel.send(msg)

def auth(user_id, level_required):
	cursor.execute(
		'''SELECT Level FROM "main.Auth"
		WHERE User = ?;''', (user_id,)
	)
	try:
		level = int(cursor.fetchone()[0])
	except:
		level = 0

	if level >= level_required:
		return True
	else:
		return False

def set_auth(user_id, set_level):
	cursor.execute(
		'''SELECT Level FROM "main.Auth"
		WHERE User = ?;''', (user_id,)
	)
	try:
		level = int(cursor.fetchone()[0])
		cursor.execute(
			'''UPDATE "main.Auth"
			SET Level = ?
			WHERE User = ?;''', (set_level, user_id)
		)
	except:
		cursor.execute(
			'''INSERT INTO "main.Auth" (User, Level)
			VALUES (?, ?);''',
			(user_id, set_level)
		)
	conn.commit()

def process(msg):
	if msg.content == '?':
		return '__**Command-Usage**__\n```Markdown\n# Add a song to the recommendation pool:\n\nadd;<artist>;<title>;<link>\n\n\n# Post a recommendation to Twitter:\n\nrec;[random/;<artist>;<title>]\n\n\n# List songs by given criteria\n\nlist;[all/id;<id>/artist;<artist>/title;<title>]\n```'

	elif msg.content.lower().startswith('add;'):
		if not auth(msg.author.id, 1):
			return 'Sorry, your authorization level is insufficient for this command.'

		try:
			r_artist = msg.content.split(';')[1]
			r_title = msg.content.split(';')[2]
			r_link = msg.content.split(';')[3]
		except:
			return 'The message format is invalid. Type \'?\' for help.'

		cursor.execute(
			'''SELECT * FROM "main.Songs"
			WHERE Artist = ? COLLATE NOCASE
			AND Title = ? COLLATE NOCASE;''', (r_artist, r_title)
		)
		rows = cursor.fetchone()
		try:
			r_songid = rows[0]
			r_artist = rows[1]
			r_title = rows[2]
			return 'The specified song already exists: **'+str(r_artist)+' - '+str(r_title)+'** (ID: '+str(r_songid)+')'
		except:
			pass

		cursor.execute("""SELECT LinkTypeID FROM "main.LinkTypes" WHERE ? REGEXP Regex;""", (r_link,))
		linktypeid = cursor.fetchone()[0]

		cursor.execute(
			'''INSERT INTO "main.Songs" (Artist, Title, User, Timestamp)
			VALUES (?, ?, ?, ?);''',
			(r_artist, r_title, msg.author.id, time.time())
		)
		cursor.execute(
			'''INSERT INTO "main.Links" (Link, LinkTypeID, SongID)
			VALUES (?, ?, last_insert_rowid());''',
			(r_link, linktypeid)
		)
		conn.commit()

		return 'Successfully added **'+r_artist+' - '+r_title+'** to the recommendation pool.'

	elif msg.content.lower().startswith('rec;'):
		if not auth(msg.author.id, 2):
			return 'Sorry, your authorization level is insufficient for this command.'

		if msg.content.lower().split(';')[1] == 'random':
			cursor.execute(
				'''SELECT * FROM "main.Songs"
				WHERE SongID IN (SELECT SongID FROM "main.Songs" WHERE Posted IS NULL ORDER BY RANDOM() LIMIT 1);'''
			)

		else:
			try:
				r_artist = msg.content.split(';')[1]
				r_title = msg.content.split(';')[2]
			except:
				return 'The message format is invalid. Type \'?\' for help.'

			cursor.execute(
				'''SELECT * FROM "main.Songs"
				WHERE Artist = ? AND Title = ?;''', (r_artist, r_title)
			)

		rows = cursor.fetchone()

		try:
			r_songid = rows[0]
			r_artist = rows[1]
			r_title = rows[2]
			r_posted = rows[3]
		except:
			return 'No suitable songs have been found in the database.'

		cursor.execute('''
            SELECT l.Link,lt.TypeName FROM "main.Links" AS l
            JOIN "main.LinkTypes" AS lt ON l.LinkTypeID = lt.LinkTypeID
            WHERE SongID = ? AND TypeName = "YouTube";''', (r_songid,)
        )
		r_links = cursor.fetchone()
		r_link = r_links[0]

		print(pf('Tweet')+t.tweet(''+r_artist+' - '+r_title+'\n\n'+r_link))

		cursor.execute(
            '''UPDATE "main.Songs"
			SET Posted = ?
			WHERE SongID = ?;''', (time.time(), r_songid)
        )
		conn.commit()

		return 'Successfully posted **'+r_artist+' - '+r_title+'** to Twitter.'

	elif msg.content.lower().startswith('list;'):
		if not auth(msg.author.id, 1):
			return 'Sorry, your authorization level is insufficient for this command.'

		if msg.content.lower().split(';')[1] == 'all':
			cursor.execute(
				'''SELECT * FROM "main.Songs";'''
				)
		else:
			try:
				searchby = msg.content.split(';')[1]
				searchfor = msg.content.split(';')[2]
			except:
				return 'The message format is invalid. Type \'?\' for help.'

			if searchby.lower() == 'id':
				searchby = 'SongID'
			elif searchby.lower() == 'artist':
				searchby = 'Artist'
			elif searchby.lower() == 'title':
				searchby = 'Title'
			else:
				return 'The search criteria is invalid. Type \'?\' for help.'

			cursor.execute(
				'''SELECT * FROM "main.Songs"
				WHERE {} = ? COLLATE NOCASE;'''.format(searchby), (searchfor,)
			)

		rows = cursor.fetchall()

		if rows != []:
			overflow = 0
			slist = 'These songs match your criteria:\n\n'
			for item in rows:
				if len(slist+'`['+str(item[0])+']` '+str(item[1])+' - '+str(item[2])+'\n') <= 1980:
					slist = slist+'`['+str(item[0])+']` '+str(item[1])+' - '+str(item[2])+'\n'
				else:
					overflow += 1

			if overflow == 0:
				return slist
			else:
				return slist + '\n*... and '+str(overflow)+' more*'
		else:
			return 'No suitable songs have been found in the database.'

	elif msg.content.lower().startswith('delete;'):
		if not auth(msg.author.id, 2):
			return 'Sorry, your authorization level is insufficient for this command.'

		try:
			id = int(msg.content.split(';')[1])
		except:
			return 'The message format is invalid. Type \'?\' for help.'

		try:
			confirmed = False
			if msg.content.split(';')[2] == 'confirm':
				confirmed = True
		except:
			pass

		cursor.execute(
			'''SELECT * FROM "main.Songs"
			WHERE SongID = ?;''', (id,)
		)

		rows = cursor.fetchall()

		if rows != []:
			if confirmed == False:
				delmsg = '**You are about to delete:**\n\n'
				delmsg = delmsg+'`['+str(rows[0][0])+']` '+str(rows[0][1])+' - '+str(rows[0][2])+'\n'
				delmsg = delmsg+'\nAre you *absolutely sure* you want to delete this song?\nConfirm by typing `delete;'+str(id)+';confirm`'
				return delmsg
			else:
				cursor.execute(
		            '''DELETE FROM "main.Songs"
					WHERE SongID = ?;''', (id,)
		        )
				conn.commit()
				return 'You have successfully deleted **'+str(rows[0][1])+' - '+str(rows[0][2])+'** from the database.'
		else:
			return 'Unable to find ID `'+str(id)+'` in the database.'

	else:
		return 'Unable to process the message. Type \'?\' for help.'

@client.event
async def on_message(message):
	channel = message.channel
	mcl = message.content.lower()
	try:
		print(pf('Log')+str(message.author)+': '+message.content)
	except:
		print(pf('Log')+'[!]: Log failed due to unicode error.')
	if message.author == client.user:
		return
	global whitelist
	if whitelist == True and not auth(message.author.id, 1):
		await send(channel, 'Sorry, I may only talk to authorized users.')
		return

	if mcl.startswith('.'):
		if auth(message.author.id, 3):
			cmd = mcl.split(' ')[0]

			if cmd == '.stop':
				await send(channel, 'Client logout called.', 'cmd_i')
				await client.logout()
			elif cmd == '.ping':
				await send(channel, 'Pong!', 'cmd_i')
			elif cmd == '.i':
				print(pf('i')+'Message ignored.')
			elif cmd == '.api':
				await send(channel, discord.__version__, 'cmd_i')
			elif cmd == '.cid':
				await send(channel, str(message.channel.id), 'cmd_i')
			elif cmd == '.uid':
				await send(channel, str(message.author.id), 'cmd_i')
			elif cmd == '.tweet':
				print(pf('Tweet')+t.tweet(message.content[7:]))
				await send(channel, 'Twitter status update called.', 'cmd_tweet')
			elif cmd == '.auth':
				try:
					set_auth(int(message.content.split(' ')[1]), int(message.content.split(' ')[2]))
					await send(channel, 'Permission level successfully updated.', 'cmd_i')
				except:
					await send(channel, 'Level and UserID must be integers.', 'cmd_e')
				else:
					await send(channel, 'Invalid command.', 'cmd_e')
		else:
			await send(channel, 'Sorry, your authorization level is insufficient for this command.')

	elif mcl == 'hello!':
		await send(channel, 'Hi there!')
	elif mcl == 'id':
		await send(channel, 'Here\'s your User-ID: '+str(message.author.id))

	else:
		await send(channel, process(message))

@client.event
async def on_ready():
	print(pf('i')+'> Username: '+client.user.name+'\n'+pf('i')+'> User-ID: '+str(client.user.id))
	print(pf('DONE')+'Taki ready!\n')

print(pf('^-^/')+'Taki starting up!')
print(pf('i')+'Logging into discord...')
client.run(discord_token)
