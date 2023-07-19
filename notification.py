#!/usr/bin/python
'''
Created on 2023/07/18

@author: ZL Chen
@title: Teams Notification
'''

import os, requests, pymsteams, sys

class notify_by_pymsteams(object):
	def __init__(self):
		pass
	def main(self, teams_webhook):
		self.teams_post(teams_webhook)
	def teams_post(self, teams_webhook):
		content = pymsteams.connectorcard(teams_webhook)
		content.title('Code-Review + 1')
		content.text('oe22_obmc_review - 23')
		content.addLinkButton('oe22_obmc_review - 23', 'http://10.10.95.52:8088/job/oe22_obmc_review/23/')
		content.send()

class notify_by_requests(object):
	def __init__(self):
		pass
	def main(self, teams_webhook):
		self.teams_post(teams_webhook)
	def teams_post(self, teams_webhook):
		message = {
			'title': 'Code-Review + 1',
			'text': 'http://10.10.95.52:8088/job/oe22_obmc_review/23/',
		}
		response = requests.post(teams_webhook, json=message)
		if response.status_code == 200:
			print('Success')
		else:
			print('Fail', response.text)

class notify_by_curl(object):
	def __init__(self):
		pass
	def main(self, teams_title, teams_description, teams_link, teams_webhook):
		self.teams_post(teams_title, teams_description, teams_link, teams_webhook)
	def teams_post(self, teams_title, teams_description, teams_link, teams_webhook):
		message = {
			"type": "message",
			"attachments": [
				{
				"contentType": "application/vnd.microsoft.card.adaptive",
					"content": {
						"$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
						"type": "AdaptiveCard",
						"version": "1.4",
							"body": [
							{
								"type": "TextBlock",
								"text": teams_description,
								"wrap": 'true'
							}
						],
							"actions": [
							{
								"type": "Action.OpenUrl",
								"title": teams_title,
								"url": teams_link
							}
						]
					}
				}
			]
		}
		content_post = 'curl -H \"Content-Type:application/json\" -d \"' + str(message) + '\" ' + teams_webhook
		os.system(content_post)

if __name__ == '__main__':
	# python notification.py 'Title: Code-Review + 1' 'Description: Description' 'http://10.10.95.52:8088/job/oe22_obmc_review/23/' 
	# 'https://asus.webhook.office.com/webhookb2/08e42c77-7185-4cae-ad87-1ff3a4855166@301f59c4-c269-4a66-8a8c-f5daab211fa3/IncomingWebhook/cd614c68599345ceac62f82437a9d096/ba639ed9-4805-4b69-bd25-8f3fd4c30042'
	teams_title = sys.argv[1]
	teams_description = sys.argv[2]
	teams_link = sys.argv[3]
	teams_webhook = sys.argv[4]
	n = notify_by_pymsteams()
	n.main(teams_webhook)
	n = notify_by_requests()
	n.main(teams_webhook)
	n = notify_by_curl()
	n.main(teams_title, teams_description, teams_link, teams_webhook)