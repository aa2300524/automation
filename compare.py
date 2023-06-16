#!/usr/bin/python
'''
Created on 2023/06/13

@author: ZL Chen
@title: Compare Data
'''

from time import sleep
from re import findall

class compare_data(object):
	def read_data(self):
		try:
			with open('cppcheck_scan_file.txt', 'r+') as cppcheck_scan_file:
				cppcheck_scan_file = cppcheck_scan_file.readlines()
				for scan in range(len(cppcheck_scan_file)):
					cppcheck_scan_file[scan] = cppcheck_scan_file[scan].split('\n')[0].split('/')[-1]
					print(cppcheck_scan_file[scan])
					with open('cppcheck_result.xml', 'r+') as cppcheck_result:
						cppcheck_result = cppcheck_result.readlines()
						for result in range(len(cppcheck_result)):
							if cppcheck_scan_file[scan] in cppcheck_result[result]:
								print(cppcheck_result[result])
								find_data_int = cppcheck_scan_file[scan] + r':(\d{1,}):(\d{1,}):'
								# print(find_data_int)
								contentRex = findall(find_data_int, cppcheck_result[result])
								if len(contentRex) == 0:
									break
								else:
									contentRex = contentRex[:]
									len_contentRex = len(contentRex)-1
									re_contentRex = contentRex[len_contentRex]
									print(re_contentRex[0], re_contentRex[1])
		except Exception as e:
			print(e)

if __name__ == "__main__":
	compare = compare_data()
	compare.read_data()