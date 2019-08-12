#!/usr/bin/env python
# -*- coding: utf-8 -*-
#=========================================================================
#
#
# Author: xxx
# Date: 2018-08-12:10:22:32
#
#=========================================================================

from __future__ import print_function
from __future__ import division

import os
import sys
import jieba
import MySQLdb
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
  

from absl import flags
from absl import logging

FLAGS = flags.FLAGS
import synonyms  # https://github.com/huyingxi/Synonyms
import numpy
import unittest

compare_ = lambda x,y,z: "%s vs %s: %f" % (x, y, synonyms.compare(x, y, seg=z)) + "\n" +"*"* 30 + "\n"

stopwords = []
for word in open('stopwords.txt', 'r'):
    stopwords.append(word.strip())

def is_similar(s2,mywords):
    i = 0
    for words in s2:
        for myword in mywords:
            if synonyms.compare1(myword, words, seg=False) > 0.7:
                i = 1
                break
    return i

def is_in_sentence(sen2,mywords):
    i = 0
    for myword in mywords:
        if myword in sen2:
            i = 1
            break
    return i

def is_in_list(s2,mywords):
    i = 0
    for words in s2:
        for myword in mywords:
            if myword == words or myword+"s" == mywords or myword+"es" == mywords or myword+"d" == mywords or myword+"ed" == mywords:
                i = 1
                break
    return i

def is_sort(interval,s2,mywords1,mywords2):
    list1 = []
    list2 = []
    for myword1 in mywords1:
        for j in range(len(s2)):
            if myword1 in s2[j]:
                # print (j)
                list1.append(j)

    for myword2 in mywords2:
        for m in range(len(s2)):
            if myword2 in s2[m]:
                # print ('aaa')
                # print (m)
                list2.append(m)

    i = 0
    for listnum1 in list1:
        for listnum2 in list2:
            if (listnum2-listnum1) > 0 and (listnum2-listnum1)<interval:
                i = 1
                break
    # print(i)
    return i

def detect(sen2):
	s2 = sen.split(' ')
	n = 0
	while 1:
		if n >= len(s2):
			break
		else:
			if s2[n] in stopwords:
				s2.remove(s2[n])
				n = 0
			else:
				n = n + 1
				
	if len(s2) > 0:
		# print(s2)
		result = ''

		# 1、ad disruption
		behavior11 = is_in_list(s2, ["ad"])
		behavior12 = is_in_list(s2, ["ads"])
		if behavior11 == 1 and "notification" not in sen2:
			result = result + ',' + "(ad disruption)"
		elif behavior12 == 1 and "notification" not in sen2:
			result = result + ',' + "(ad disruption)"

		# 2、virus
		behavior21 = is_in_list(s2, ["virus"])
        	behavior22 = is_in_list(s2, ["trojan"])
        	behavior23 = is_in_list(s2, ["malware"])
		if behavior21 == 1:
			result = result + ',' + "(virus)"
		elif behavior22 == 1:
			result = result + ',' + "(virus)"
		elif behavior23 == 1:
			result = result + ',' + "(virus)"

		# 3、privacy leak
		behavior31 = is_in_list(s2, ["steal"])
        	behavior32 = is_in_list(s2, ["info", "infomation", "data", "file"])
        	behavior33 = is_sort(3, s2, ["steal"], ["info", "infomation"])
        	behavior34 = is_in_list(s2, ["data", "photo", "file", "backup"])
        	behavior35 = is_in_list(s2, ["miss", "lost"])
        	behavior36 = is_sort(3, s2, ["data", "photo", "file", "backup"], ["miss", "lost"])
		if behavior31 == 1 and behavior32 == 1 and behavior33 == 1:
			result = result + ',' + "(privacy leak)"
		elif behavior34 == 1 and behavior35 == 1 and behavior36 == 1:
			result = result + ',' + "(privacy leak)"

		# 4、browser
		behavior41 = is_in_list(s2, ["browser", "bookmark"])
        	behavior42 = is_in_list(s2, ["modify", "hijack"])
		if behavior41 == 1 and behavior42 == 1:
			result = result + ',' + "(browser)"

		# 5、bad performance
		behavior51 = is_in_list(s2, ["phone"])
        	behavior52 = is_in_list(s2, ["crash", "stuck"])
        	behavior53 = is_in_list(s2, ["signal", "wifi"])
        	behavior54 = is_similar(s2, ["weak"])
        	behavior55 = is_in_list(s2, ["CPU"])
        	behavior56 = is_similar(s2, ["slow"])
        	behavior57 = is_in_list(s2, ["battery"])
        	behavior57 = is_similar(s2, ["consume"])
		if behavior51 == 1 and behavior52 == 1:
			result = result + ',' + "(bad performance)"
		elif behavior53 == 1 and behavior54 == 1:
			result = result + ',' + "(bad performance)"
		elif behavior55 == 1 and behavior56 == 1:
			result = result + ',' + "(bad performance)"
		elif behavior57 == 1:
			result = result + ',' + "(bad performance)"

		# 6、payment
		behavior61 = is_in_list(s2, ["fraud", "cheat", "deceive"])
        	behavior62 = is_in_list(s2, ["bill", "money", "payment", "$"])
		
		if behavior61 == 1 and behavior62 == 1:
			result = result + ',' + "(payment)"

		# 7、network traffic
		behavior71 = is_in_list(s2, ["network", "traffic"])
        	behavior72 = is_similar(s2, ["consume"])
		
		if behavior71 == 1 and behavior72 == 1:
			result = result + ',' + "(network traffic)"
		
		# 8、drive-by download
		behavior81 = is_in_list(s2, ["download", "install"])
        	behavior82 = is_in_list(s2, ["app", "plug-in", "it"])
        	behavior83 = is_in_list(s2, ["force", "let", "induce"])

		if behavior81 == 1 and behavior82 == 1 and behavior83 == 1:
			result = result + ',' + "(drive-by download)"

		# 9、hidden app
		behavior91 = is_in_list(s2, ["icon", "app"])
        	behavior92 = is_in_list(s2, ["disappear", "hidden", "not find"])
		if behavior91 == 1 and behavior92 == 1:
			result = result + ',' + "(hidden app)"
		

		# 10、fail to uninstall
		behavior100 = is_in_list(s2, ["fail"])
        	behavior101 = is_in_list(s2, ["cannot"])
        	behavior102 = is_in_list(s2, ["how"])
        	behavior103 = is_in_list(s2, ["forbid"])
        	behavior104 = is_in_list(s2, ["uninstall", "remove"])
        	behavior105 = is_sort(2, s2, ["cannot"], ["uninstall", "remove"])
        	behavior106 = is_sort(2, s2, ["how"], ["uninstall", "remove"])
        	behavior107 = is_sort(3, s2, ["fail"], ["uninstall", "remove"])
        	behavior108 = is_sort(3, s2, ["uninstall", "remove"], ["fail"])
        	behavior109 = is_sort(3, s2, ["forbid"], ["uninstall", "remove"])
        	behavior110 = is_sort(3, s2, ["uninstall", "remove"], ["forbid"])
		if behavior100 == 1 and behavior104 == 1 and (behavior107 == 1 or behavior108 == 1):
			result = result + ',' + "(fail to uninstall)"
		elif behavior103 == 1 and behavior104 == 1 and (behavior109 == 1 or behavior110 == 1):
			result = result + ',' + "(fail to uninstall)"
		elif behavior101 == 1 and behavior104 == 1 and behavior105 == 1:
			result = result + ',' + "(fail to uninstall)"
		elif behavior102 == 1 and behavior104 == 1 behavior106 == 1:
			result = result + ',' + "(fail to uninstall)"
			
		# 11、powerboot
		behavior110 = is_in_list(s2, ["powerboot"])
		if behavior110 == 1:
			result = result + ',' + "(powerboot)"

		# 12、fail to start
		behavior120 = is_in_list(s2, ["crash", "stuck"])
        	behavior121 = is_in_list(s2, ["stop"])
        	behavior122 = is_in_list(s2, ["running"])
        	behavior123 = is_in_list(s2, ["fail", "cannot"])
        	behavior124 = is_in_list(s2, ["start"])
        	behavior125 = is_sort(2, s2, ["fail", "cannot"], ["start"])
        	behavior126 = is_in_list(s2, ["exception"])
		if behavior120 == 1 and "phone" not in sen2:
			result = result + ',' + "(fail to start)"
		elif behavior121 == 1 and behavior122 == 1:
			result = result + ',' + "(fail to start)"
		elif behavior123 == 1 and behavior124 == 1 and behavior125 == 1:
			result = result + ',' + "(fail to start)"
		elif behavior126 == 1:
			result = result + ',' + "(fail to start)"

		# 13、fail to exit
		behavior130 = is_in_list(s2, ["cannot", "exit", "close", "shut"])
        	behavior131 = is_sort(2, s2, ["cannot"], ["exit", "close", "shut"])
		if behavior130 == 1 and behavior131 == 1:
			result = result + ',' + "(fail to exit)"

		# 14、 retrieve content
		behavior140 = is_in_list(s2, ["404", "blank"])
        	behavior141 = is_in_list(s2, ["fail", "cannot", "data"])
        	behavior142 = is_sort(2, s2, ["fail", "cannot"], ["data"])
		
		if behavior140 == 1:
			result = result + ',' + "(retrieve content)"
		elif behavior141 == 1 and behavior142 == 1:
			result = result + ',' + "(retrieve content)"

		# 15、notification ad
		behavior150 = is_in_list(s2, ["notification"])
        	behavior151 = is_in_list(s2, ["ad", "ads", "full", "remove"])
		if behavior150 == 1 and behavior151 == 1:
			result = result + ',' + "(notification ad)"

		# 16、fail to login
		behavior160 = is_in_list(s2, ["cannot", "fail", "how"])
        	behavior161 = is_in_list(s2, ["login", "register"])
		if behavior160 == 1 and behavior161 == 1:
			result = result + ',' + "(fail to login)"
		
		# 17、add shortcuts
		behavior170 = is_in_list(s2, ["add", "create"])
        	behavior171 = is_in_list(s2, ["shortcut", "icon"])
		if behavior170 == 1 and behavior171 == 1:
			result = result + ',' + "(add shortcuts)"

		# 18、fail to install
		behavior180 = is_in_list(s2, ["cannot", "fail", "how"])
        	behavior181 = is_in_list(s2, ["install"])
		if behavior180 == 1 and behavior181 == 1:
			result = result + ',' + "(fail to install)"

		# 19、redirection
		behavior190 = is_in_list(s2, ["redirect"])
        	behavior191 = is_in_list(s2, ["other"])
		if behavior190 == 1 and behavior191 == 1:
			result = result + ',' + "(redirection)"

		# 20、vulgar content
		behavior200 = is_in_sentence(sen2, [" nude", "masturbat", "racist", " porn", "creep", "pervert", "pedophile", "horny", "penis", " dick", " sex"])
		if behavior200 == 1:
			result = result + ',' + "(vulgar content)"

		# 21、inconsistency
		behavior210 = is_in_list(s2, ["inconsistent"])
        	behavior211 = is_in_list(s2, ["not"])
        	behavior212 = is_in_list(s2, ["describe"])
		if behavior210 == 1:
			result = result + ',' + "(inconsistency)"
		elif behavior211 == 1 and behavior212 == 1:
			result = result + ',' + "(inconsistency)"

		# 22、background
		behavior220 = is_in_list(s2, ["itself", "background", "alwalys"])
        	behavior221 = is_in_list(s2, ["download", "sms", "backup"])
		if behavior220 == 1 and behavior221 == 1:
			result = result + ',' + "(background)"

		# 23、permission abuse
		behavior230 = is_sort(3, s2, ["ask", "unncessary"], ["permission"])
		behavior231 = is_sort(3, s2, ["require", "need", "want", "give"], ["permission", "access to"])
		behavior232 = is_sort(3, s2, ["permission", "access to"], ["require", "need", " file", "photo", "record", "media", "picture"])
		if behavior230 == 1:
			result = result + ',' + "(permission abuse)"
		elif behavior231 == 1 or behavior232 == 1:
			result = result + ',' + "(permission abuse)"

		# 24、update
		behavior240 = is_sort(3, s2, ["update"], ["other"])
        	behavior241 = is_in_list(s2, ["update", "other"])
		if behavior240 == 1 and behavior241 == 1:
			result = result + ',' + "(update)"

		# 25、repackage
		behavior250 = is_in_list(s2, ["piracy", "repackage", "copy", "plagiarize"])
		if behavior250 == 1:
			result = result + ',' + "(repackage)"
			
		# 26、ranking fraud
		behavior260 = is_in_list(s2, ["comment", "review"])
        	behavior261 = is_in_list(s2, ["fake", "sponsor", "sell", "buy"])
		if behavior260 and behavior261 == 1:
			result = result + ',' + "(ranking fraud)"
			
			
		print(result)
   

if __name__ == '__main__':
    detect('your comment here')
