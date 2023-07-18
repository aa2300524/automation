#!/usr/bin/python
'''
Created on 2023/07/18

@author: ZL Chen
@title: Teams Notification
'''

import os, requests, pymsteams, configparser

config = configparser.ConfigParser()
config.read('notification.ini')

class notify_by_pymsteams(object):
	def __init__(self):
		pass
	def main(self):
		self.teams()
	def teams(self):
		webhook_url = config.get('setting', 'webhook_url')
		message = {
			'text': 'Gerrit',
			'title': 'Notification',
		}
		content = pymsteams.connectorcard(webhook_url)
		content.title("This is my message title")
		content.text('ZL')
		content.addLinkButton("This is the button Text", "https://github.com/rveachkc/pymsteams/")
		content.send()

class notify_by_requests(object):
	def __init__(self):
		pass
	def main(self):
		self.teams()
	def teams(self):
		webhook_url = config.get('setting', 'webhook_url')
		message = {
			'text': 'Gerrit',
			'title': 'Notification',
		}
		response = requests.post(webhook_url, json=message)
		if response.status_code == 200:
			print('Success')
		else:
			print('Fail', response.text)

class notify_by_curl(object):
	def __init__(self):
		pass
	def main(self):
		self.teams()
	def teams(self):
		webhook_url = config.get('setting', 'webhook_url')
		message = {
			'text': 'Gerrit',
			'title': 'Notification',
		}
		content = 'curl -H \"Content-Type:application/json\" -d \"' + str(message) + '\" ' + webhook_url
		os.system(content)

if __name__ == '__main__':
	n = notify_by_pymsteams()
	n.main()
	n = notify_by_requests()
	n.main()
	n = notify_by_curl()
	n.main()