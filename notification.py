#!/usr/bin/python3
'''
Created on 2023/06/07

@author: ZL Chen
@title: Notification
'''

import requests, configparser

config = configparser.ConfigParser()
config.read('notification.ini')
default_token = 'jQvdFCXCvsVIAIlSQEIWnw5Vwc3LOmOitcph96Ik3IH'

class notification(object):
	def line(self, message):
		headers = {
			'Authorization': 'Bearer ' + default_token, # ESBG Group Token
			'Content-Type': 'application/x-www-form-urlencoded'
		}
		params = {'message': message}
		try:
			r = requests.post('https://notify-api.line.me/api/notify', headers=headers, params=params)	
		except:
			print('Status code number:', r.status_code)  #200

if __name__ == '__main__':
	notify = notification()
	notify.line(config['line']['message'])