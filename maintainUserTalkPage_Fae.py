#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
maintainUserTalkPage_Fae.py
https://commons.wikimedia.org/wiki/User_talk:Fae/talk_page_trimmer

Trim the most ghastly of templates from user talk to something more palattable
Intended to run hourly in local crontab.

Date: July 2014, Dec 2014, Feb 2015
	2016 August Convert to core.
	2018 April Additional requests, add Dw image source
	2019 November Version to run on Ubuntu, running with Faebot, add riley

Author: Fae, http://j.mp/faewm

Permissions: CC-BY-SA-NC
'''

import pywikibot, sys, urllib2, urllib, re, time
import platform

userpages = [
		u"F\xe6",
		"Russavia",
		"Josve05a",
		"Dcoetzee",
		"Reguyla",
		"Rcbutcher",
		"Wuestenigel",
		"Panoramio upload bot", # Request by Steinsplitter
		"GifTagger", # Requested by Jeff G.
		"Artix Kreiger", # Global lock, lots of notices
		"~riley", # https://commons.wikimedia.org/w/index.php?diff=377380291
		]

# Add physical machine to edit comment
myhost = platform.node()
if myhost == 'raspberrypi':
	myhost = ' ({})'.format(myhost)
elif myhost == 'ashley-ThinkPad-X220':
	myhost = ' (ThinkPad-X220)'
elif myhost[:5] == 'tools':
	myhost = ' ([[Toolforge:|Toolforge]])'
else:
	myhost = ''

site = pywikibot.getSite('commons', 'commons')

for page in userpages:
	mypage = pywikibot.Page(site, 'User talk:' + page)
	html = mypage.get()
	action = ["[[User talk:Fae/talk page trimmer|Trim templates]]"]
	go=False
	
	# Check for and also DR lists
	regex = "\nAnd also: \n((\* \[\[:File:[^\]\n]*\]\] ?\n)+)"
	if re.search(regex, html):
		html = re.sub(regex, r"\nAnd also:\n{{cot}}\n\1{{cob}}", html)
		go = True
		action.append("Collapse 'also' list")
	
	# Check for DRs
	regex = "\n?\n(\{\{Autotranslate\|1=File:([^\|]*?)\|2=\|3=\|base=Idw\}\})"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\n{{lf|\2}}<br/>\n[[Commons:Deletion requests/File:\2]]", html)
			go = True
			action.append("Trim DR notice for file")
	
	regex = "\n(\{\{Autotranslate\|1=Template:([^\|]*?)\|2=\|3=\|base=Idw\}\})"
	if re.search(regex, html):
			html = re.sub(regex, r"\n<!--Boiler plate notice reduced: \1-->\n{{tlx|\2}}<br/>\n[[Commons:Deletion requests/Template:\2]]", html)
			go = True
			action.append("Trim DR notice for template")
	
	regex = "\n(\{\{Autotranslate\|1=\|2=([^\|]*?)\|3=plural\|base=Idw\}\})"
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
			html = re.sub(regex, r"\1[[:File:\2|\3]]&mdash;[[Phabricator:T113878|]]\4", html)
			go = True
			action.append("[[Phabricator:T113878]] root cause likely to be WMF server failure, reduce to Flickr PhotoID")

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
	
	# Duplicate
	regex = r"\n\{\{.utotranslate\|base=Speedynote\|1=File:([^\|]*?)\|2=This file is a(n .*exact duplicate\]\]| duplicate)[^\[]*?\[\[:File:([^\]]*?)\]\][^\|\}]*?\}\}"
	if re.search(regex, html):
		html = re.sub(regex, r"\n<!--Boiler plate notice reduced-->\n{{lf|\1}} &rarr; {{lf|\3}}", html)
		go = True
		action.append("Trim duplicate notice")
	
	# Speedywhat
	regex = "\n(\{\{[aA]utotranslate\|1=File:([^\|]*?)\|base=speedywhat[^\|\}]*\}\})"
	if re.search(regex, html):
		html = re.sub(regex, r"\n{{green|<small>{{tlx|Speedywhat}} notice removed. Deleting admin please note, if you want anything to be learned from your decision to delete, using the standard [[Commons:Deletion requests|]] procedure gives several days for non-sysops to examine the history and details of the files to be deleted. Skipping this collegiate step, means that despite investing effort into deleting specific files, you are unlikely to see any related improvements to the way upload projects work. -- Faebot</small>}}\n<!--Boiler plate notice reduced: \1-->\n\n{{lf|\2}}", html)
		go = True
		action.append("Trim speedywhat notice")
	
	# Please link images
	regex = "\n== \{\{Autotranslate\|base=Please link images/heading\}\} ==\n\n\{\{Autotranslate\|1=\|base=Please link images\}\}.*?\(UTC\)"
	if re.search(regex, html, flags=re.DOTALL):
		html = re.sub(regex, "", html)
		go = True
		action.append("Trim please link images tip, not useful on this talk page")

	# Please link images
	regex = "\n(\{\{[aA]utotranslate\|1=File:([^\|]*?)\|base=Please link images[^\|\}]*\}\})"
	if re.search(regex, html):
		html = re.sub(regex, r"\n{{green|<small>{{tlx|Please link images}}</small>}}\n<!--Boiler plate notice reduced: \1-->\n\n{{lf|\2}}", html)
		go = True
		action.append("Trim Please link images")
	
	if go:
			action = " | ".join(action) + myhost
			pywikibot.setAction(action)
			mypage.put(html)