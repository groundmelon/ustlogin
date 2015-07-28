#!/usr/bin/python

import requests
import HTMLParser
import sys
import getpass
import os
import subprocess

default_itsc_username = os.environ['UST_ITSC_USERNAME']

ANSI_COLOR_RED     = "\x1b[31m"
ANSI_COLOR_GREEN   = "\x1b[32m"
ANSI_COLOR_YELLOW  = "\x1b[33m"
ANSI_COLOR_BLUE    = "\x1b[34m"
ANSI_COLOR_MAGENTA = "\x1b[35m"
ANSI_COLOR_CYAN    = "\x1b[36m"
ANSI_COLOR_RESET   = "\x1b[0m"

def print_color(s, color):
	print("%s%s%s"%(color, s, ANSI_COLOR_RESET))

class USTLoginPageParser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.post_data = dict()
		self.post_url = None

	def handle_starttag(self, tag, attrs):
		if tag=='input':
			key = None
			value = None
			for attr in attrs:
				if attr[0]=='name':
					key = attr[1]
				elif attr[0]=='value':
					value = attr[1]

			print('post data [%s]:%s'%(key, value))
			self.post_data[key] = value
		elif tag=='form':
			value = None
			for attr in attrs:
				if attr[0]=='action':
					 value = attr[1]
			print("post url: <%s>"%value)
			self.post_url = value


	def handle_endtag(self, tag):
		pass

	def handle_data(self, data):
		pass

	def get_post_url(self):
		return self.post_url

	def get_post_data(self):
		return self.post_data

def main():
	print("Default ITSC username is \"%s\""%default_itsc_username)
	print_color("Requesting login information...", ANSI_COLOR_YELLOW)
	r = requests.get('http://www.ust.hk', verify=False)
	if r.status_code!=200:
		print("r.status_code = %d", r.status_code)
		return -1
	print_color("Response received successfully.", ANSI_COLOR_GREEN)

	parser = USTLoginPageParser()
	print("------------------------------------")
	parser.feed(r.text)
	print("------------------------------------")
	post_data = parser.get_post_data()
	post_url = parser.get_post_url()

	if (not post_data.has_key('mac')) and (not post_data.has_key('token')):
		msgstr = "ERROR: Cannot find login form. You might have been logged in."
		print_color(msgstr, ANSI_COLOR_RED)
		subprocess.Popen(['notify-send', msgstr])
		return -1

	post_data['user'] = raw_input('ITSC Username [%s]:'%default_itsc_username)
	post_data['pass'] = getpass.getpass('ITSC Password:')

	if not post_data['user']:
		post_data['user'] = default_itsc_username

	post_data['mode_login.x'] = '18'
	post_data['mode_login.y'] = '16'
	post_data.pop('mode_login')

	print_color("Submitting login information...", ANSI_COLOR_YELLOW)
	r = requests.post(post_url, data=post_data, verify=False)
	msgstr = "Login information submitted with return code %d"%r.status_code
	print_color(msgstr, ANSI_COLOR_GREEN)
	subprocess.Popen(['notify-send', msgstr])

	print("-------------- response ----------------")
	print(r.text)
	print("----------------------------------------")

	return

if __name__ == "__main__":
	sys.exit(main())
