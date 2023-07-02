#!/usr/bin/python3
'''
Created on 2023/06/07

@author: ZL Chen
@title: Notification
'''

import requests, configparser

config = configparser.ConfigParser()
config.read('notification.ini')
default_token = 'EsZWfD53xuk5F9KGaHHWltdOeukodqRMBHNWDoXY0v7'

class notification(object):
	def line(self, message):
		headers = {
			'Authorization': 'Bearer ' + default_token, # ESBU Group Token
			'Content-Type': 'application/x-www-form-urlencoded'
		}
		params = {'message': message}
		try:
			r = requests.post('https://notify-api.line.me/api/notify', headers=headers, params=params)	
		except:
			print('Status code number:', r.status_code)  # type: ignore #200

if __name__ == '__main__':
	notify = notification()
	notify.line(config['line']['message'])