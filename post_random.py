import twitter as t
import os
import random
from shutil import copyfile

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

print(t.tweet(r_artist+' - '+r_title+'\n\n'+r_link))
copyfile('data/pending/'+r_artist+'_'+r_title+'.txt', 'data/posted/'+r_artist+'_'+r_title+'.txt')
os.remove('data/pending/'+r_artist+'_'+r_title+'.txt')
print('> File transferred from /pending/ to /posted/.')
print('Successfully posted '+r_artist+' - '+r_title+' to Twitter.')
