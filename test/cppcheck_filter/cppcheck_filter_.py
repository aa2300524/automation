#!/usr/bin/python
'''
Created on 2023/06/21

@author: ZL Chen
@title: cppcheck filter
'''

import re, time, gerrit

class cppcheck_filter(object):
	def __init__(self):
		self.GERRIT_HOST = 'GERRIT_HOST' + '='
		self.GERRIT_PROJECT = 'GERRIT_PROJECT' + '='
		self.GERRIT_BRANCH = 'GERRIT_BRANCH' + '='
		self.GERRIT_CHANGE_ID = 'GERRIT_CHANGE_ID' + '='
		self.GERRIT_PATCHSET_REVISION = 'GERRIT_PATCHSET_REVISION' + '='
		self.rest_api_path = ''

	def cppcheck_result_xml(self):
		try:
			content = self.jenkins_parameter()
			counter = list()
			with open('cppcheck_scan_file.txt', 'r') as cppcheck_scan_file:
				cppcheck_scan_file = cppcheck_scan_file.readlines()
				print(cppcheck_scan_file, 'cppcheck_scan_file')
				for scan in range(len(cppcheck_scan_file)):
					self.rest_api_path = cppcheck_scan_file[scan].replace('/', '%2F').replace('\n', '')
					return_rest_api_request = cppcheck.rest_api_request(content, self.rest_api_path)
					print(return_rest_api_request, 'return_rest_api_request')
					_cppcheck_scan_file = cppcheck_scan_file[scan].split('\n')[0].split('/')[-1]
					print(_cppcheck_scan_file, '_cppcheck_scan_file')
					print('----------------------------------------------------------------------------------')
					with open('cppcheck_result.xml', 'r') as cppcheck_result:
						cppcheck_result = cppcheck_result.readlines()
						for result in range(len(cppcheck_result)):
							# print(_cppcheck_scan_file, cppcheck_result[result].split('\n')[0])
							if _cppcheck_scan_file in cppcheck_result[result]:
								find_data_int = _cppcheck_scan_file + r':(\d{1,}):'
								contentRex = re.findall(find_data_int, cppcheck_result[result].split('\n')[0])
								print(contentRex, 'contentRex')
								if len(contentRex) == 0:
									pass
								else:
									contentRex = contentRex[:]
									len_contentRex = len(contentRex)-1
									re_contentRex = contentRex[len_contentRex]
									# print(re_contentRex[0], re_contentRex[1], 're_contentRex[0], re_contentRex[1]')
									counter.append(re_contentRex)
							else:
								pass
						print(counter)
					time.sleep(1)
					print('-------------------------------------------------------------------------')
					if len(counter) != 0:
						list_source = return_rest_api_request
						list_destination = counter
						list_compare = list(set(list_destination).difference(set(list_source)))
						counter_re = list()
						with open('cppcheck_result.xml', 'r') as cppcheck_result:
							cppcheck_result = cppcheck_result.readlines()
							for n in range(len(list_compare)):
								print(list_compare[n])
								for result in range(0, len(cppcheck_result), 3):
									cppcheck_result_total = cppcheck_result[result] + cppcheck_result[result+1] + cppcheck_result[result+2]
									print(cppcheck_result_total, 'ddddddddddddddddddddddddddddddddddddddd')
									if _cppcheck_scan_file in cppcheck_result_total:
										# find_data_int = _cppcheck_scan_file + r':(\d{1,}):'
										find_data_int = r'(.*)' + _cppcheck_scan_file + r':' + list_compare[n] + r':(\d*):(.*\n.*\n.*[\^])'
										print(find_data_int, 'find_data_intfind_data_intfind_data_intfind_data_intfind_data_intfind_data_intfind_data_int')
										# contentRex = re.findall(find_data_int, cppcheck_result[result].split('\n')[0])
										contentRex = re.findall(find_data_int, cppcheck_result_total)
										print(contentRex, 'contentRexcontentRexcontentRexcontentRexcontentRexcontentRexcontentRexcontentRexcontentRex')
										if len(contentRex) == 0:
											pass
										else:
											contentRex = contentRex[:]
											len_contentRex = len(contentRex)-1
											re_contentRex = contentRex[len_contentRex]
											# print(re_contentRex)
											# print(len(re_contentRex[:]))
											# for l in range(len(re_contentRex[:])):
											# 	print(re_contentRex[l])
												# re_contentRex += re_contentRex[l]
											print(re_contentRex, 're_contentRexre_contentRexre_contentRexre_contentRexre_contentRex')
											temp = ''
											for l in range(len(re_contentRex[:])):
												# print('test')
												temp = temp + re_contentRex[l]
												# print(temp)
												if l == 0:
													temp = temp + _cppcheck_scan_file + ':' + list_compare[n] + ':'
													print(temp, 'temptemptemptemptemptemptemptemptemptemptemptemptemp')
												if l == 1:
													temp = temp + ':'

											re_contentRex = temp
											print(re_contentRex, 're_contentRexre_contentRexre_contentRexre_contentRexre_contentRexre_contentRexre_contentRex')
											# print(re_contentRex[0], re_contentRex[1], 're_contentRex[0], re_contentRex[1]')
											counter_re.append(str(re_contentRex[:]))
											# # counter_re.append(int(re_contentRex[1]))
											print(counter_re, 'ddddddddddddddddd')


								# print(counter_re, 'ddddddddddddddddd')
								# time.sleep(10000)	
								# with open('cppcheck_result.xml', 'r') as check_result_xml:
								# 	lines = check_result_xml.readlines()
								# 	# print(lines, len(lines))
								# 	for a in range(len(lines)):
								# 		for b in range(len(list_compare)):
								# 			if list_compare[b] in lines[a]:
								# 				del lines[a]
								# 				with open('cppcheck_result.txt', 'w') as file:
								# 					file.writelines(lines)
								# 		if a == len(lines) - 1:
								# 			break
								# time.sleep(1)
											with open('cppcheck_result.xml', 'r') as check_result_xml:
												lines = check_result_xml.readlines()
												print(lines, 'ddddddddddddddddd')
												for a in range(0, len(lines), 3):
													print(counter_re[0].split('\n')[0])
													# lines_total = lines[a] + lines[a+1] + lines[a+2]
													# print(lines_total)
													# print(type(counter_re[0]))
													# print(type(lines_total))
													print(lines[a:a+3][0])
													if counter_re[0].split('\n')[0] in lines[a:a+3][0]:
														print('testtest')
														del lines[a:a+3]
														with open('cppcheck_result.txt', 'w') as file:
															file.writelines(lines)
													print('uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
					else:
						print('counter is None')
						time.sleep(1)

		except:
			pass

	def jenkins_parameter(self):
		try:
			content = list()
			with open('jenkins_env.log', 'r') as file:
				jenkins_readlines = file.readlines()
				jenkins_len = len(jenkins_readlines)
				for parameter in range(jenkins_len):
					jenkins_readlines_parameter = jenkins_readlines[parameter].split('\n')[0]
					if self.GERRIT_HOST in jenkins_readlines_parameter:
						jenkins_readlines_parameter = jenkins_readlines_parameter.replace(self.GERRIT_HOST, '')
						content.append(jenkins_readlines_parameter)
					elif self.GERRIT_PROJECT in jenkins_readlines_parameter:
						jenkins_readlines_parameter = jenkins_readlines_parameter.replace(self.GERRIT_PROJECT, '')
						content.append(jenkins_readlines_parameter)
					elif self.GERRIT_BRANCH in jenkins_readlines_parameter:
						jenkins_readlines_parameter = jenkins_readlines_parameter.replace(self.GERRIT_BRANCH, '')
						content.append(jenkins_readlines_parameter)
					elif self.GERRIT_CHANGE_ID in jenkins_readlines_parameter:
						jenkins_readlines_parameter = jenkins_readlines_parameter.replace(self.GERRIT_CHANGE_ID, '')
						content.append(jenkins_readlines_parameter)
					elif self.GERRIT_PATCHSET_REVISION in jenkins_readlines_parameter:
						jenkins_readlines_parameter = jenkins_readlines_parameter.replace(self.GERRIT_PATCHSET_REVISION, '')
						content.append(jenkins_readlines_parameter)
					else:
						pass
			return content
		except Exception as e:
			print(e)

	def rest_api_request(self, content, rest_api_path):
		# print(self.GERRIT_HOST, content[-1])
		# print(self.GERRIT_PROJECT, content[0])
		# print(self.GERRIT_BRANCH, content[-2])
		# print(self.GERRIT_CHANGE_ID, content[1])
		# print(self.GERRIT_PATCHSET_REVISION, content[2])
		uri = 'http://10.10.95.52:8080/a/changes' \
				'/ESR1-511-X4TF~develop-ami-rr13.3-esr1-511-x4tf~I97eb4366b79ebd879921c9d03b1dd7b177ae2436' \
				'/revisions/7a46283666ec00c5d944de51bd6696a7ea13b0fe/files' \
					'/src_override%2Fsource%2Fipmi_dev-13.11.25.0.0-src%2Fdata%2FOemPlatform.h/diff'
		uri = 'http://' + content[-1] + ':8080/a/changes' + '/' + content[0] + '~' + content[-2] + '~' + content[1] + \
				'/revisions/' + content[2] + '/files' + '/src_override%2Fsource%2Fipmi_dev-13.11.25.0.0-src%2Fdata%2FOemPlatform.h/diff'
		uri = 'http://' + content[-1] + ':8080/a/changes' + '/' + content[0] + '~' + content[-2] + '~' + content[1] + \
				'/revisions/' + content[2] + '/files' + '/' + rest_api_path + '/diff'
		uri = '/changes' + '/' + content[0] + '~' + content[-2] + '~' + content[1] + \
				'/revisions/' + content[2] + '/files' + '/' + rest_api_path + '/diff'
		client = gerrit.GerritClient(base_url='http://10.10.95.52:8080/', username='zl', password='Zl@123')
		response_content = client.get(uri)['content']
		return_git_diff_parser = self.git_diff_parser(response_content)
		time.sleep(1)
		return return_git_diff_parser
	
	def git_diff_parser(self, response_content):
		git_diff_counter = 0
		git_diff_list = list()
		for content_n in range(len(response_content)):
			if 'ab' in response_content[content_n]:
				# print(len(response_content[content_n]['ab']), 'ab')
				git_diff_counter += len(response_content[content_n]['ab'])
			elif 'b' in response_content[content_n]:
				# print(len(response_content[content_n]['b']), 'b')
				for b in range(len(response_content[content_n]['b'])):
					git_diff_counter += 1
					git_diff_list.append(git_diff_counter)
			else:
				pass
		# print(git_diff_list, 'git_diff_list')
		return git_diff_list

	def main(self):
		self.cppcheck_result_xml()

if __name__ == '__main__':
	cppcheck = cppcheck_filter()
	cppcheck.main()