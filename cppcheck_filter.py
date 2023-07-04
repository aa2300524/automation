#!/usr/bin/python
'''
Created on 2023/06/21

@author: ZL Chen
@title: cppcheck filter
'''

from gerrit import GerritClient
from time import sleep
from re import findall
from sys import argv

class cppcheck_filter(object):
	def __init__(self):
		self.GERRIT_HOST = 'GERRIT_HOST' + '='
		self.GERRIT_PROJECT = 'GERRIT_PROJECT' + '='
		self.GERRIT_BRANCH = 'GERRIT_BRANCH' + '='
		self.GERRIT_CHANGE_ID = 'GERRIT_CHANGE_ID' + '='
		self.GERRIT_PATCHSET_REVISION = 'GERRIT_PATCHSET_REVISION' + '='
		self.rest_api_path = ''

	def main(self, argv_1, argv_2, argv_3):
		self.cppcheck_result_xml(argv_1, argv_2, argv_3)

	def cppcheck_result_xml(self, argv_1, argv_2, argv_3):
		try:
			content = self.jenkins_parameter(argv_3)
			counter = list()
			print(content)
			with open(argv_2, 'r') as cppcheck_scan_file:
				cppcheck_scan_file = cppcheck_scan_file.readlines()
				print(cppcheck_scan_file)
				for scan in range(len(cppcheck_scan_file)):
					self.rest_api_path = cppcheck_scan_file[scan].replace('/', '%2F').replace('\n', '')
					print(self.rest_api_path)	# src_override%2Fsource%2Fipmi_dev-13.11.25.0.0-src%2Fdata%2FOemPlatform.h
					_cppcheck_scan_file = cppcheck_scan_file[scan].split('\n')[0].split('/')[-1]
					print(_cppcheck_scan_file)	# OemPlatform.h
					return_rest_api_request = cppcheck.rest_api_request(content, self.rest_api_path)
					print('REST API', return_rest_api_request)	# [37, 38]
					with open(argv_1, 'r') as cppcheck_result:
						cppcheck_result = cppcheck_result.readlines()
						# print(cppcheck_result)	# 檔案內容讀每一行內容出來
						print('******************************************************************************************************')
						for result in range(len(cppcheck_result)):
							if _cppcheck_scan_file in cppcheck_result[result]:
								find_data_int = _cppcheck_scan_file + r':(\d{1,})'
								# print(find_data_int)	# 正規化語法 maintenance_fwupdate.c:(\d{1,})
								# print(cppcheck_result[result].split('\n')[0])
								# src_override/source/spx_restservice-13.30.49.0.0-src/data/maintenance_fwupdate.c:18:16: warning: Redundant assignment of 'matches' to itself. [selfAssignment]
								contentRex = findall(find_data_int, cppcheck_result[result].split('\n')[0])
								# print(contentRex)	# 每行找到的資料讀取
								if len(contentRex) == 0:
									pass
								else:
									counter.append(contentRex[0])
									# print(counter)	# ['18']
						#---------------------------------------------#
						buffer = list()	# 由小排到大
						for sort in range(len(counter)):
							buffer.append(int(counter[sort]))
						counter = sorted(buffer)
						buffer.clear()
						for sort in range(len(counter)):
							buffer.append(str(counter[sort]))
						counter = buffer
						#---------------------------------------------#
						print('counter:', counter)
						# ['18', '68', '92', '129', '176', '321', '364', '387', '477', '539', '718', '740', '770', '791', '816', '165', '168', '169', '170', '171', '312', '735', '515', '513', '161', '812', '84', '826']
					if len(counter) != 0:
						set_return_rest_api_request = list(return_rest_api_request) # type: ignore
						# print('REST API', set_return_rest_api_request)
						#---------------------------------------------#
						buffer = list()
						for sort in range(len(counter)):
							buffer.append(int(counter[sort]))
						counter.clear()
						counter = buffer
						#---------------------------------------------#
						print('counter:', counter)
						set_return_rest_api_request = set(return_rest_api_request) # type: ignore
						set_counter = set(counter)
						# print(set_return_rest_api_request, 'set_return_rest_api_request')
						# print(set_counter, 'set_counter')
						compare = list(set(set_counter).difference(set(set_return_rest_api_request)))	# 留下要刪除的 Flag
						# compare = list(set_counter - set_return_rest_api_request)
						print('compare:', compare)
						#---------------------------------------------#
						buffer = list()	# 由小排到大
						for sort in range(len(compare)):
							buffer.append(int(compare[sort]))
						compare.clear()
						compare = sorted(buffer)
						buffer.clear()
						for sort in range(len(compare)):
							buffer.append(str(compare[sort]))
						compare = buffer
						#---------------------------------------------#
						print('compare:', compare)
						# ['84', '826', '387', '791', '321', '312', '477', '169', '170', '171', '718', '740', '513', '168', '364', '539', '161', '770', '129', '18', '176', '735', '68', '165', '92', '816', '515', '812']
						# sleep(1)
						print('******************************************************************************************************')
						# sleep(10000)
						counter_re = list()
						with open(argv_1, 'r') as cppcheck_result:
							cppcheck_result = cppcheck_result.readlines()	# 讀取原始 XML 每一行資料
							for n in range(len(compare)):	# 讀取 compare 後需要刪除的資料
								try:
									for result in range(0, len(cppcheck_result), 3):
										cppcheck_result_total = cppcheck_result[result] + cppcheck_result[result + 1] + cppcheck_result[result + 2]
										print(cppcheck_result_total)	# 一次讀取三行資料
										if _cppcheck_scan_file in cppcheck_result_total:
											print(_cppcheck_scan_file)	# OemPlatform.h
											find_data_int = r'(.*)' + _cppcheck_scan_file + r':' + compare[n] + r':(\d*):(.*\n.*\n.*[\^])'
											contentRex = findall(find_data_int, cppcheck_result_total)
											print(contentRex)	#	如果 != 0 進入 else
											if len(contentRex) != 0:
												contentRex = contentRex[:]
												len_contentRex = len(contentRex)-1
												re_contentRex = contentRex[len_contentRex]
												temp = ''
												for l in range(len(re_contentRex[:])):
													temp = temp + re_contentRex[l]
													if l == 0:
														temp = temp + _cppcheck_scan_file + ':' + compare[n] + ':'
													if l == 1:
														temp = temp + ':'
												re_contentRex = temp
												print(re_contentRex)	# 需要刪除的檔案
												counter_re.append(str(re_contentRex[:]))
												print(counter_re)
												with open(argv_1, 'r') as check_result_xml:
													lines = check_result_xml.readlines()
													for a in range(0, len(lines), 3):												
														print(counter_re[0].split('\n')[0])
														print(lines[a:a+3][0].split('\n')[0])
														# sleep(1)
														if counter_re[0].split('\n')[0] == lines[a:a+3][0].split('\n')[0]:	# 判斷是否同樣 Flag
															# sleep(1)
															print('OK TO DELETE DATA.')
															del lines[a:a+3]
															with open(argv_1, 'w') as file:
																file.writelines(lines)	# 檔案更新
															break
												counter_re = list()
										cppcheck_result_total = ''
								except:
									print('list index out of range')
									pass
					else:
						print('counter & compare are empty')
					counter.clear()	# 清空 list
		except Exception as e:
			print(e)

	def jenkins_parameter(self, argv_3):
		try:
			content = list()
			with open(argv_3, 'r') as file:
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
		try:
			uri = '/changes' + '/' + content[0] + '~' + content[-2] + '~' + content[1] + \
					'/revisions/' + content[2] + '/files' + '/' + rest_api_path + '/diff'
			client = GerritClient(base_url='http://10.10.95.52:8080/', username='zl', password='Zl@123')
			response_content = client.get(uri)['content']
			return_git_diff_parser = self.git_diff_parser(response_content)
			return return_git_diff_parser
		except Exception as e:
			print(e)
	
	def git_diff_parser(self, response_content):
		git_diff_counter = 0
		git_diff_list = list()
		try:
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
			return git_diff_list
		except Exception as e:
			print(e)

if __name__ == '__main__':
	cppcheck = cppcheck_filter()
	argv_1 = argv[1]	# cppcheck_result.xml
	argv_2 = argv[2]	# cppcheck_scan_file.txt
	argv_3 = argv[3]	# jenkins_env.log
	cppcheck.main(argv_1, argv_2, argv_3)