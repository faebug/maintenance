#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
maintainUserTalkPage_Fae.py
https://commons.wikimedia.org/wiki/User_talk:Fae/talk_page_trimmer

Trim the most ghastly of templates from user talk to something more palattable
Intended to run hourly or less in local crontab, later pushed out to ToolForge.

Date: July 2014, Dec 2014, Feb 2015
	2016 August Convert to core.
	2018 April Additional requests, add Dw image source
	2019 November Version to run on Ubuntu, running with Faebot, add riley
		 Add over transcluded and WMF banned accounts
	2019 December
		 Add ALL parameter to include all listed pages

Example crontab
13,28,43,57 * * * * cd '/home/pi/pywikibot/core'; nice -n 20 python pwb.py maintainUserTalkPage_Fae.py -dir:faebot 1>/dev/null 2>&1

Example commandline
python pwb.py maintainUserTalkPage_Fae.py ALL -dir:faebot

Author: Fae, http://j.mp/faewm

Permissions: CC-BY-SA-NC
'''

import pywikibot, sys, urllib2, urllib, re, time
import platform, os.path
from random import randint

userpages = [
		"Panoramio upload bot", # Request by Steinsplitter
		"GifTagger", # Requested by Jeff G.
		]

userpagesold = [ # Less active talk pages
		"Dcoetzee",
		"Reguyla",
		"Rcbutcher",
		"Wuestenigel",
		"Artix Kreiger", # Global lock, lots of notices
		"Russavia",
		]

# Add physical machine to edit comment
myhost = platform.node()
if myhost == 'raspberrypi':
	if os.path.isfile('/sys/firmware/devicetree/base/model'):
		if re.search('Pi Zero', open('/sys/firmware/devicetree/base/model', 'r').read() ):
			myhost = 'Pi Zero'
		if re.search('Pi 3 Model B', open('/sys/firmware/devicetree/base/model', 'r').read() ):
			myhost = 'Pi 3'
	myhost = ' ({})'.format(myhost)
elif myhost == 'ashley-ThinkPad-X220':
	myhost = ' (ThinkPad-X220)'
elif myhost[:5] == 'tools':
	myhost = ' ([[Toolforge:|Toolforge]])'
else:
	myhost = ''

site = pywikibot.getSite('commons', 'commons')

override = False
if len(sys.argv)>2:
	if sys.argv[1] == "ALL":
		override = True

# Add from user category
for u in pywikibot.Category(site, "Category:Talk page trimmer").articles():
	if u.title().split(':')[1] not in userpages and not re.search('/', u.title()):
		if u.namespace().id == 3:
			userpages.append(u.title()[10:])
		elif u.namespace().id == 2:
			userpages.append(u.title()[5:])

# Add older pages, 10% of the time
if override or randint(1,10) == 1:
	userpages.extend( userpagesold )

# Active! Add banned users, 1% of the time
if override or randint(1,100) == 1:
	banned = [u.title()[5:] for u in pywikibot.Category(site, "Category:Commons users banned by the WMF").articles() if u.title()[5:] not in userpages]
	userpages.extend( banned )
# Long term blocked users, 5% of the time
if override or randint(1,20) == 1:
	blocked = u"Juiced lemon,Worldenc,Lycaon,Massimilianogalardi,MakBot,MaybeMaybeMaybe,Saibo,Unauthorized Bot,FA2010,Scotire,Erwin Lindemann,Steinbeisser~commonswiki,FSV,Orrling,EChastain,Soranoch,Hiku2,Blackwhiteupl,苏州河,Co9man,Look2See1,Kharkivinite,OSX II,FlickrWarrior,Dr. Bernd Gross,Amitie 10g,TohaomgBot,BulbaBot,GH1903892AH".split(',')
	userpages.extend( blocked )

# Add over-transcluded list as of 2019 after notifications, 5% of the time
if override or randint(1,20) == 1:
	transcluded = u"Grzesiek Kurka,Inefable001,Olaf Kosinsky (usurped),Germrai,Posterrr,Mti,Keres 40,Daniel Ventura,Dabit100,Star61,Talmoryair,Luissilveira,CoughingCookieHeart,Huthayfah Halabiyeh,Ser Amantio di Nicolao,Константин Филиппов,Vladimir OKC,Garitan,BugWarp,Bergamasco70,S. DÉNIEL,Shahen Araboghlian,Khangul,BezPRUzyn,Avril1975,Noniki,Tatiana Matlina,Jcpag2012,Xpotty,Ввласенко,Daising Shiumia MA,Daniel V.,Zarateman,WDKeeper,Tigran Mitr am,SreeBot".split(',')
	transcluded.append(u'Mindmatrix (2019, part I)') # arg, accounts with commas
	userpages.extend( transcluded )

for page in userpages:
	mypage = pywikibot.Page(site, 'User talk:' + page)
	html = mypage.get()
	action = ["[[User talk:Fae/talk page trimmer|Trim templates]]"]
	go=False
	
	# Check for any 'and also' DR lists
	regex = "\nAnd also: \n((\* \[\[:File:[^\]\n]*\]\] ?\n)+)"
	if re.search(regex, html):
		html = re.sub(regex, r"\nAnd also:\n{{cot}}\n\1{{cob}}", html)
		go = True
		action.append("Collapse 'also' list")
	
	# Check for DRs
	regex = "\n?\n(\{\{.utotranslate\|1=File:([^\|]*?)\|2=\|3=\|base=Idw\}\})"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\n{{lf|\2}}<br/>\n[[Commons:Deletion requests/File:\2]]", html)
			go = True
			action.append("Trim DR notice for file")
	else: # Missing params, maybe manually added
		regex = "\n?\n(\{\{.utotranslate\|1=File:([^\|]*?)\|base=Idw\}\})"
		if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\n{{lf|\2}}<br/>\n[[Commons:Deletion requests/File:\2]]", html)
			go = True
			action.append("Trim DR notice for file")
	regex = "\n(\{\{.utotranslate\|1=Template:([^\|]*?)\|2=\|3=\|base=Idw\}\})"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\n{{tlx|\2}}<br/>\n[[Commons:Deletion requests/Template:\2]]", html)
			go = True
			action.append("Trim DR notice for template")
	
	regex = "\n(\{\{.utotranslate\|1=\|2=([^\|]*?)\|3=plural\|base=Idw\}\})"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\nBundle DR:<br/>\n[[Commons:Deletion requests/\2]]<br/>\n", html)
			go = True
			action.append("Trim bundle DR notice")
	
	# Image license
	# == {{Autotranslate|1=File:.. (14598046958).jpg|base=Image license/heading}} ==
	regex = "\n(\{\{Autotranslate\|1=File:([^\|]*?)\|base=Image license\}\} ?\n? ?)"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->", html)
			go = True
			action.append("Trim copyright notice")
	# Image license + pid
	regex = "(== )\{\{Autotranslate\|1=File:([^\|]*?\((\d{11})\).jpg)\|base=Image license/heading\}\}( ==)"
	if re.search(regex, html):
			html = re.sub(regex, r"\1[[:File:\2|\3]]\4", html)
			go = True
			action.append("Possible server failure, reduce to Flickr PhotoID")

	# Image license + BHL
	regex = "(== )\{\{Autotranslate\|1=File:([^\|]*?(BHL\d{7,8}).jpg)\|base=Image license/heading\}\}( ==)"
	if re.search(regex, html):
			html = re.sub(regex, r"\1[[:File:\2|\3]]&mdash;[[Phabricator:T113878|]]\4", html)
			go = True
			action.append("[[Phabricator:T113878]] root cause likely to be WMF server failure, reduce to BHL PageID")

	# Copyvio
	regex = "\n(\{\{.utotranslate\|1=File:([^\|]*?)(\| ?2 ?=.*)?\|base=Copyvionote[^\|\}]*\}\})"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\n{{lf|\2}}", html)
			go = True
			action.append("Trim copyvio notice for file")

	# Image source
	regex = "\n(\{\{Autotranslate\|1=File:([^\|]*?)\|base=Image source[^\|\}]*\}\})"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\n{{lf|\2}}", html)
			go = True
			action.append("Trim image source notice")

	# Image Dw source
	regex = "\n(\{\{Autotranslate\|1=File:([^\|]*?)\|base=Dw image source(\|2=)?[^\|\}]*\}\})"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\n{{lf|\2}}", html)
			go = True
			action.append("Trim derivative work source notice")

	# Image permission
	regex = "\n(\{\{Autotranslate\|1=File:([^\|]*?)\|base=Image permission[^\|\}]*\}\})"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\n{{lf|\2}}", html)
			go = True
			action.append("Trim image permission notice")
	
	# Speedy CSD F10 Personal photo
	regex = r"\n\{\{.utotranslate\|base=Speedynote\|1=File:([^\|]*?)\|2=.*Personal photos of[^\|\}]*?\}\}"
	if re.search(regex, html):
		html = re.sub(regex, r"\n<span style='color:green'>[[template:Speedynote|Speedy]] notice for [[COM:CSD#F10|F10 personal photos by non-contributors]] reduced.</span>\n<br/>[[:File:\1|\1]]", html)
		go = True
		action.append("Trim [[COM:CSD#F10]] speedy notice")

	# Speedy duplicate
	regex = r"\n\{\{.utotranslate\|base=Speedynote\|1=File:([^\|]*?)\|2=This file is a(n .*exact duplicate\]\]| duplicate)[^\[]*?\[\[:File:([^\]]*?)\]\][^\|\}]*?\}\}"
	if re.search(regex, html):
		html = re.sub(regex, r"\n<!--Boiler plate notice reduced-->\n{{lf|\1}} &rarr; {{lf|\3}}", html)
		go = True
		action.append("Trim speedy duplicate notice")
	
	# Speedywhat
	regex = "\n(\{\{[aA]utotranslate\|1=File:([^\|]*?)\|base=speedywhat[^\|\}]*\}\})"
	if re.search(regex, html):
		html = re.sub(regex, r"\n<span style='color:green'>[[template:Speedywhat|Speedywhat]] notice removed.</span>\n<!--Boiler plate notice reduced: \1-->\n\n{{lf|\2}}", html)
		go = True
		action.append("Trim [[template:Speedywhat]] notice")

	'''-- Tips and other non-warnings --'''
	
	# Please link images
	regex = "\n== \{\{Autotranslate\|base=Please link images/heading\}\} ==\n\n\{\{Autotranslate\|1=\|base=Please link images\}\}.*?\(UTC\)"
	if re.search(regex, html, flags=re.DOTALL):
		html = re.sub(regex, "", html)
		go = True
		action.append("Trim [[template:please link images]] tip, not useful on this talk page")

	regex = "\n(\{\{[aA]utotranslate\|1=File:([^\|]*?)\|base=Please link images[^\|\}]*\}\})"
	if re.search(regex, html):
		html = re.sub(regex, r"\n<span style='color:green'>Trimmed category tip, [[template:please link images|]]</span>\n<!--Boiler plate notice reduced: \1-->\n\n{{lf|\2}}", html)
		go = True
		action.append("Trim [[template:Please link images]] tip")
	
	# Fair use tip
	regex = "\{\{.utotranslate\|base=No fair use\}\}"
	if re.search(regex, html):
		html = re.sub(regex, r"<span style='color:green'>Trimmed tip, [[template:No fair use|no fair use]]</span>", html)
		go = True
		action.append("Trim [[template:No fair use]] tip")

	# Welcome
	regex = "\{\{(Welcome\|[^\}]*)\}\}\n"
	if re.search(regex, html):
		html = re.sub(regex, u"<span style='color:green'>Trimmed [[template:Welcome|welcome]] notice</span>\n", html)
		go = True
		action.append("Trim [[template:Welcome]] notice")

	# QIC promoted
	regex = "(\{\{(QICpromoted\|File:([^\|]*))\}\}\n)"
	if re.search(regex, html):
		html = re.sub(regex, r"<!--Boiler plate notice reduced:\n\2-->\nQIC promoted:\n*[[:File:\3|\3]]\n", html)
		go = True
		action.append("Trim QICpromoted")
	regex = "(\{\{(QICpromoted\|File:([^\|]*)\|.*?UTC\)\s*)\}\}\n)"
	if re.search(regex, html):
		html = re.sub(regex, r"<!--Boiler plate notice reduced:\n\2-->\nQIC promoted:\n*[[:File:\3|\3]]\n", html)
		go = True
		action.append("Trim QICpromoted")
	
	if go:
			action = " | ".join(action) + myhost
			pywikibot.setAction(action)
			try:
				mypage.put(html)
			except Exception:
				pass
