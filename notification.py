#!/usr/bin/python
'''
Created on 2023/07/18

@author: ZL Chen
@title: Teams Notification
'''

import os, requests, pymsteams, configparser
# import os, configparser, sys

config = configparser.ConfigParser()
config.read('notification.ini')

class notify_by_pymsteams(object):
	def __init__(self):
		pass
	def main(self):
		self.teams_post()
	def teams_post(self):
		webhook_url = config.get('setting', 'webhook_url')
		content = pymsteams.connectorcard(webhook_url)
		content.title('Code-Review + 1')
		content.text('oe22_obmc_review - 23')
		content.addLinkButton('oe22_obmc_review - 23', 'http://10.10.95.52:8088/job/oe22_obmc_review/23/')
		content.send()

class notify_by_requests(object):
	def __init__(self):
		pass
	def main(self):
		self.teams_post()
	def teams_post(self):
		webhook_url = config.get('setting', 'webhook_url')
		message = {
			'title': 'Code-Review + 1',
			'text': 'http://10.10.95.52:8088/job/oe22_obmc_review/23/',
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
		self.teams_post()
	def teams_post(self):
		webhook_url = config.get('setting', 'webhook_url')
		message = {
			'title': 'Code-Review + 1',
			'text': 'http://10.10.95.52:8088/job/oe22_obmc_review/23/',
		}
		content_post = 'curl -H \"Content-Type:application/json\" -d \"' + str(message) + '\" ' + webhook_url
		print(content_post)
		os.system(content_post)

if __name__ == '__main__':
	n = notify_by_pymsteams()
	n.main() # type: ignore
	n = notify_by_requests()
	n.main() # type: ignore
	n = notify_by_curl()
	n.main() # type: ignore