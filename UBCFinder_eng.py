#!/usr/bin/env python
# -*- coding: utf-8 -*-
#=========================================================================
#
#
# Author: xxx
# Date: 2018-08-13:8:14:12
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
            if (listnum2-listnum1) > 0 and (listnum2-listnum1)<=interval:
                i = 1
                break
    # print(i)
    return i

def detect(sen2):
	s2 = sen2.split(' ')
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
		adrule1 = is_in_list(s2, ["ads"])
		if adrule1 == 1 and "notification" not in sen2:
			result = result + ',' + "(ad disruption)"

		# 2、virus
		virusrule1 = is_in_list(s2, ["virus"])
        	virusrule12 = is_in_list(s2, ["trojan"])
        	virusrule3 = is_in_list(s2, ["malware"])
		if (virusrule1+virusrule2+virusrule3) != 0:
			result = result + ',' + "(virus)"

		# 3、privacy leak
		privacyrule1 = is_sort(3, s2, ["steal"], ["info"])
        	privacyrule2 = is_sort(3, s2, ["steal"], ["information"])
        	privacyrule3 = is_sort(4, s2, ["steal"], ["data"])
        	privacyrule4 = is_sort(3, s2, ["steal"], ["file"])
        	privacyrule5 = is_sort(4, s2, ["data"], ["miss"])
        	privacyrule6 = is_sort(5, s2, ["photo"], ["miss"])
		privacyrule7 = is_sort(7, s2, ["file"], ["miss"])
		privacyrule8 = is_sort(6, s2, ["backup"], ["miss"])
		privacyrule9 = is_sort(4, s2, ["data"], ["lost"])
        	privacyrule10 = is_sort(5, s2, ["photo"], ["lost"])
		privacyrule11 = is_sort(6, s2, ["file"], ["lost"])
		privacyrule12 = is_sort(7, s2, ["backup"], ["lost"])
		if (privacyrule1+privacyrule2+privacyrule3+privacyrule4+privacyrule5+privacyrule6+privacyrule7+privacyrule8+privacyrule9+privacyrule10+privacyrule11+privacyrule12) != 0:
			result = result + ',' + "(privacy leak)"

		# 4、browser
		browserrule1 = is_sort(2, s2, ["modify"], ["browser"])
		browserrule2 = is_sort(2, s2, ["modify"], ["bookmark"])
		browserrule3 = is_sort(2, s2, ["hijack"], ["browser"])
        	browserrule4 = is_sort(2, s2, ["hijack"], ["bookmark"])
		if (browserrule1+browserrule2+browserrule3+browserrule4) != 0:
			result = result + ',' + "(browser)"

		# 5、bad performance
		performrule1 = is_sort(3, s2, ["phone"], ["crash"])
        	performrule2 = is_sort(3, s2, ["phone"], ["stuck"])
        	performrule3 = is_sort(3, s2, ["signal"], ["weak"])
        	performrule4 = is_sort(3, s2, ["wifi"], ["weak"])
        	performrule5 = is_sort(3, s2, ["CPU"], ["slow"])
        	performrule6 = is_sort(3, s2, ["consume"], ["battery"])
		if (performrule1+performrule2+performrule3+performrule4+performrule5+performrule6) != 0:
			result = result + ',' + "(bad performance)"

		# 6、payment
		paymentrule1 = is_sort(7, s2, ["cheat"], ["bill"])
		paymentrule2 = is_sort(11, s2, ["cheat"], ["money"])
		paymentrule3 = is_sort(6, s2, ["cheat"], ["payment"])
		paymentrule4 = is_sort(9, s2, ["cheat"], ["$"])
		paymentrule5 = is_sort(12, s2, ["deceive"], ["bill"])
		paymentrule6 = is_sort(11, s2, ["deceive"], ["money"])
		paymentrule7 = is_sort(4, s2, ["deceive"], ["payment"])
		paymentrule8 = is_sort(6, s2, ["deceive"], ["$"])
		paymentrule9 = is_sort(2, s2, ["payment"], ["fraud"])
		paymentrule10 = is_sort(2, s2, ["bill"], ["fraud"])
		paymentrule11 = is_sort(15, s2, ["fraud"], ["$"])
		paymentrule12 = is_sort(17, s2, ["fraud"], ["money"])

		if (paymentrule1+paymentrule2+paymentrule3+paymentrule4+paymentrule5+paymentrule6+paymentrule7+paymentrule8+paymentrule9+paymentrule10+paymentrule11+paymentrule12) != 0:
			result = result + ',' + "(payment)"

		# 7、network traffic
		networkrule1 = is_sort(3, s2, ["consume"], ["traffic"])
        	networkrule2 = is_sort(3, s2, ["consume"], ["network"])
		
		if (networkrule1+networkrule2) != 0:
			result = result + ',' + "(network traffic)"
		
		# 8、drive-by download
		driverule1 = is_sort(2, s2, ["download"], ["itself"])
		driverule2 = is_sort(4, s2, ["force"], ["download"])
		driverule3 = is_sort(4, s2, ["let"], ["download"])
		driverule4 = is_sort(3, s2, ["induce"], ["download"])
		driverule5 = is_sort(2, s2, ["install"], ["itself"])
		driverule6 = is_sort(4, s2, ["force"], ["install"])
		driverule7 = is_sort(3, s2, ["let"], ["install"])
		driverule8 = is_sort(4, s2, ["induce"], ["install"])
		driverule9 = is_sort(3, s2, ["download"], ["plug-in"])
        	driverule10 = is_sort(3, s2, ["install"], ["plug-in"])

		if (driverule1+driverule2+driverule3+driverule4+driverule5+driverule6+driverule7+driverule8+driverule9+driverule10) != 0:
			result = result + ',' + "(drive-by download)"

		# 9、hidden app
		behavior91 = is_in_list(s2, ["icon", "app"])
        	behavior92 = is_in_list(s2, ["disappear", "hidden", "not find"])
		if behavior91 == 1 and behavior92 == 1:
			result = result + ',' + "(hidden app)"
		

		# 10、fail to uninstall
		uninstallrule1 = is_sort(3, s2, ["fail"], ["uninstall"])
		uninstallrule2 = is_sort(4, s2, ["fail"], ["remove"])
		uninstallrule3 = is_sort(4, s2, ["uninstall"], ["fail"])
		uninstallrule4 = is_sort(5, s2, ["remove"], ["fail"])
		uninstallrule5 = is_sort(5, s2, ["cannot"], ["uninstall"])
        	uninstallrule6 = is_sort(5, s2, ["cannot"], ["remove"])
		uninstallrule7 = is_sort(6, s2, ["how"], ["uninstall"])
		uninstallrule8 = is_sort(5, s2, ["how"], ["remove"])
		uninstallrule9 = is_sort(3, s2, ["forbid"], ["uninstall"])
		uninstallrule10 = is_sort(4, s2, ["forbid"], ["remove"])
		uninstallrule11 = is_sort(4, s2, ["uninstall"], ["forbid"])
		uninstallrule12 = is_sort(3, s2, ["remove"], ["forbid"])
		if (uninstallrule1+uninstallrule2+uninstallrule3+uninstallrule4+uninstallrule5+uninstallrule6+uninstallrule7+uninstallrule8+uninstallrule9
		   +uninstallrule10+uninstallrule11+uninstallrule12) != 0:
			result = result + ',' + "(fail to uninstall)"
			
		# 11、powerboot
		powerbootrule1 = is_in_list(s2, ["powerboot"])
		if powerbootrule1 != 0:
			result = result + ',' + "(powerboot)"

		# 12、fail to start
		startrule1 = is_in_list(s2, ["crash", "stuck"])
        	startrule2 = is_sort(2, s2, ["stop"], ["running"])
        	startrule3 = is_sort(6, s2, ["running"], ["stop"])
        	startrule4 = is_sort(4, s2, ["fail"], ["start"])
        	startrule5 = is_sort(3, s2, ["cannot"], ["start"])
        	startrule6 = is_sort(7, s2, ["start"], ["fail"])
        	startrule7 = is_in_list(s2, ["exception"])
		if (startrule1+startrule2+startrule3+startrule4+startrule5+startrule6+startrule7) != 0:
			result = result + ',' + "(fail to start)"

		# 13、fail to exit
		exitrule1 = is_sort(2, s2, ["cannot"], ["exit"])
		exitrule2 = is_sort(2, s2, ["cannot"], ["close"])
		exitrule3 = is_sort(2, s2, ["cannot"], ["shut"])
        	if (exitrule1+exitrule2+exitrule3) != 0:
			result = result + ',' + "(fail to exit)"

		# 14、 retrieve content
		contentrule1 = is_in_list(s2, ["404", "blank"])
        	contentrule2 = is_sort(6, s2, ["fail"], ["data"])
        	contentrule3 = is_sort(7, s2, ["cannot"], ["data"])
		if (contentrule1+contentrule2+contentrule3) != 0:
			result = result + ',' + "(retrieve content)"

		# 15、notification ad
		notifirule1 = is_sort(3, s2, ["notification"], ["ads"])
		notifirule2 = is_sort(2, s2, ["notification"], ["full"])
		notifirule3 = is_sort(4, s2, ["remove"], ["notification"])
		if (notifirule1+notifirule2+notifirule3) != 0:
			result = result + ',' + "(notification ad)"

		# 16、fail to login
		loginrule1 = is_sort(2, s2, ["cannot"], ["login"])
		loginrule2 = is_sort(2, s2, ["cannot"], ["register"])
		loginrule3 = is_sort(3, s2, ["fail"], ["login"])
		loginrule4 = is_sort(2, s2, ["fail"], ["register"])
		loginrule5 = is_sort(5, s2, ["register"], ["fail"])
		loginrule6 = is_sort(3, s2, ["how"], ["login"])
        	loginrule7 = is_sort(3, s2, ["how"], ["register"])
		if (loginrule1+loginrule2+loginrule3+loginrule4+loginrule5+loginrule6+loginrule7) != 0:
			result = result + ',' + "(fail to login)"
		
		# 17、add shortcuts
		shorcutrule1 = is_sort(3, s2, ["add"], ["shortcut"])
		shorcutrule2 = is_sort(2, s2, ["create"], ["shortcut"])
		shorcutrule3 = is_sort(2, s2, ["create"], ["icon"])
        	shorcutrule4 = is_sort(2, s2, ["add"], ["icon"])
		if (shorcutrule1+shorcutrule2+shorcutrule3+shorcutrule4) != 0:
			result = result + ',' + "(add shortcuts)"

		# 18、fail to install
        	installrule1 = is_sort(2, s2, ["fail"], ["install"])
		installrule2 = is_sort(4, s2, ["install"], ["fail"])
		installrule3 = is_sort(2, s2, ["how"], ["install"])
		installrule4 = is_sort(3, s2, ["cannot"], ["install"])
		if (installrule1+installrule2+installrule3+installrule4) != 0:
			result = result + ',' + "(fail to install)"

		# 19、redirection
		redirectrule1 = is_sort(3, s2, ["redirect"], ["other"])
		if redirectrule1 != 0:
			result = result + ',' + "(redirection)"

		# 20、vulgar content
		vulgarrule1 = is_in_sentence(sen2, [" nude", "masturbat", "racist", " porn", "creep", "pervert", "pedophile", "horny", "penis", " dick", " sex"])
		if vulgarrule1 != 0:
			result = result + ',' + "(vulgar content)"

		# 21、inconsistency
		inconsistrule1 = is_in_list(s2, ["inconsistent"])
        	inconsistrule2 = is_sort(7, s2, ["not"], ["describe"])
		if (inconsistrule1+inconsistrule2) != 0:
			result = result + ',' + "(inconsistency)"

		# 22、background
		backgroudrule1 = is_sort(4, s2, ["alwalys"], ["download"])
		backgroudrule2 = is_sort(3, s2, ["backup"], ["itself"])
		backgroudrule3 = is_sort(5, s2, ["download"], ["background"])
		backgroudrule4 = is_sort(7, s2, ["sms"], ["background"])
		backgroudrule5 = is_sort(6, s2, ["sms"], ["itself"])
		backgroudrule6 = is_sort(5, s2, ["download"], ["itself"])
		backgroudrule7 = is_sort(3, s2, ["backup"], ["background"])
		if (backgroudrule1+backgroudrule2+backgroudrule3+backgroudrule4+backgroudrule5+backgroudrule6+backgroudrule7) != 0:
			result = result + ',' + "(background)"

		# 23、permission abuse
		permissionrule1 = is_sort(5, s2, ["ask"], ["permission"])
		permissionrule2 = is_sort(2, s2, ["unnecessary"], ["permission"])
		permissionrule3 = is_sort(6, s2, ["require"], ["permission"])
		permissionrule4 = is_sort(6, s2, ["need"], ["permission"])
		permissionrule5 = is_sort(7, s2, ["want"], ["permission"])
		permissionrule6 = is_sort(7, s2, ["give"], ["permission"])
		if (permissionrule1+permissionrule2+permissionrule3+permissionrule4+permissionrule5+permissionrule6) != 0:
			result = result + ',' + "(permission abuse)"

		# 24、update
		updaterule1 = is_sort(3, s2, ["update"], ["other"])
		if updaterule1 != 0:
			result = result + ',' + "(update)"

		# 25、repackage
		repackagerule1 = is_in_list(s2, ["piracy", "repackage", "copy", "plagiarize"])
		if repackagerule1 != 0:
			result = result + ',' + "(repackage)"
			
		# 26、ranking fraud
		rankingrule1 = is_sort(3, s2, ["fake"], ["comment"])
		rankingrule2 = is_sort(4, s2, ["sponsor"], ["comment"])
		rankingrule3 = is_sort(3, s2, ["fake"], ["review"])
		rankingrule4 = is_sort(3, s2, ["sponsor"], ["review"])
		rankingrule5 = is_sort(5, s2, ["sell"], ["comment"])
		rankingrule6 = is_sort(3, s2, ["sell"], ["review"])
		rankingrule7 = is_sort(5, s2, ["buy"], ["comment"])
		rankingrule8 = is_sort(5, s2, ["buy"], ["review"])
		if (rankingrule1+rankingrule2+rankingrule3+rankingrule4+rankingrule5+rankingrule6+rankingrule7+rankingrule8) != 0:
			result = result + ',' + "(ranking fraud)"
			
			
		print(result)
   

if __name__ == '__main__':
    detect('your comment here ')
