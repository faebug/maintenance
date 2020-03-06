# -*- coding: utf-8 -*-
NOTICE = """
Speedies_maintenance.py

Category:Candidates for speedy deletion
For relevant subcategories of speedy deletion, check the upload year and
add to tracking category for 3+ or 10+ years old files.
"""
import pywikibot, re
from sys import argv
from datetime import datetime, timedelta
from colorama import Fore, Back, Style
from colorama import init
init()

site = pywikibot.Site('commons','commons')
print Fore.GREEN
print NOTICE, Fore.WHITE

files = set()
startcatArr = """Copyright violations
Non-free logos
Copyright violations (OTRS)
Unfree Flickr files
Flickr files from bad authors
No OTRS permission
Personal files for speedy deletion
Duplicate
Image crop missing parent page
Other speedy deletions
Pending fair use deletes
Flickr images from bad authors
Advertisements for speedy deletion
Images without source""".split("\n")

catArr = startcatArr[:]
print Fore.YELLOW + "Categories", Fore.GREEN
print "\n".join(catArr)

existing = []
for cat in ["Files uploaded over 10 years ago in a speedy deletion subcategory",
			"Files uploaded over 3 years ago in a speedy deletion subcategory"]:
	existing.extend( pywikibot.Category(site, "Category:" + cat ).articles( namespaces = 6 ) )

rset = set()
count = 0
for cat in catArr:
	files = set()
	catp = pywikibot.Category(site, "Category:" + cat)
	ts3years = datetime.now() - timedelta(3*365)
	try:
		for f in catp.articles( recurse=False, namespaces=6, sortby="timestamp", endtime=ts3years ):
			try:
				if f.isRedirectPage():
					continue
				test = f.oldest_file_info.timestamp
				files.add(f)
				#print test.year, f.title()
			except Exception as e:
				print Fore.RED, str(e)
				print Fore.CYAN, f.title(), Fore.WHITE
				continue
	except Exception as e:
		print Fore.RED, str(e)
		print Fore.CYAN, cat, Fore.WHITE
	for f in files:
		count += 1
		if f in rset or f in existing:
			continue
		if f.isRedirectPage():
			continue
		'''history = f.getFileVersionHistory()
		comments = " | ".join([r['comment'] for r in history])
		users = set([r['user'] for r in history])'''
		try:
			rev = f.oldest_file_info
			age = ( datetime.now() - rev.timestamp ).days/365 
		except Exception as e:
			print Fore.RED, str(e), Fore.WHITE
			print Fore.CYAN, f.title()[5:], Fore.WHITE
			continue
		if age < 3:
			continue
		rset.add(f)
		if not f.exists():
			continue
		html = f.get()
		if re.search("Category:Speedy deletions for files over", html):
			continue
		year = rev.timestamp.year
		if age >= 10:
			print Fore.CYAN, count, Fore.YELLOW + cat, Fore.MAGENTA + f.title()[5:], Fore.GREEN, year, Fore.WHITE
			html += "\n[[Category:Files uploaded over 10 years ago in a speedy deletion subcategory|" + "{}]]".format(year)
			pywikibot.setAction("[[User:Faebot/old speedies]] | ([[Category:" + cat + "]]) add [[Category:Files uploaded over 10 years ago in a speedy deletion subcategory]]" + " {}".format(year) )
		else:
			print Fore.CYAN, count, Fore.YELLOW + cat,  Fore.YELLOW + f.title()[5:], Fore.GREEN, year, Fore.WHITE
			html += "\n[[Category:Files uploaded over 3 years ago in a speedy deletion subcategory|" + "{}]]".format(year)
			pywikibot.setAction("[[User:Faebot/old speedies]] | ([[Category:" + cat + "]]) add [[Category:Files uploaded over 3 years ago in a speedy deletion subcategory]]" + " {}".format(year) )
		f.put(html)
