#!/usr/bin/env python
# -*- coding: utf-8 -*-
#=========================================================================
#
#
# Author: xxx
# Date: 2020-08-12:10:22:32
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
	# sen2 = ''  # input: 评论
	s2 = [x for x in jieba.cut(sen2)]
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
		# 每个词进行比较
		# print(s2)
		result = ''

		# 1、ad disruption
		adrule1 = is_in_sentence(sen2, ["广告"])
		adrule11 = is_sort(7, s2, ["没", "避免", "去", "看", "无"], ["广告"])
		adrule12 = is_sort(7, s2, ["广告"], ["没", "少", "不多"])
		if adrule1 == 1 and "桌面" not in sen2 and "通知栏" not in sen2 and adrule11 != 1 and adrule12 != 1:
			result = result + ',' + "(ad disruption)"

		# 2、virus
		virusrule1 = is_in_sentence(sen2, ["病毒"])
		virusrule2 = is_in_sentence(sen2, ["木马"])
		if (virusrule1+virusrule2) != 0:
			result = result + ',' + "(virus)"

		# 3、privacy leak
		privacyrule1 = is_sort(11, s2, ["备份"], ["没有"])
		privacyrule2 = is_sort(17, s2, ["备份"], ["不见"])
		privacyrule3 = is_sort(11, s2, ["备份"], ["没"])
		privacyrule4 = is_sort(3, s2, ["数据"], ["不见"])
		privacyrule5 = is_sort(10, s2, ["数据"], ["没"])
		privacyrule6 = is_sort(1, s2, ["数据"], ["全没"])
		privacyrule7 = is_sort(6, s2, ["东西"], ["没"])
		privacyrule8 = is_sort(2, s2, ["资料"], ["没"])
		privacyrule9 = is_sort(2, s2, ["资料"], ["全没"])
		privacyrule10 = is_sort(6, s2, ["云服务"], ["不见"])
		privacyrule11 = is_sort(6, s2, ["照片"], ["没"])
		privacyrule12 = is_sort(4, s2, ["图库"], ["清理"])
		privacyrule13 = is_sort(2, s2, ["盗窃"], ["信息"])
		if (privacyrule1+privacyrule2+privacyrule3+privacyrule4+privacyrule5+privacyrule6+privacyrule7+privacyrule8+privacyrule9+privacyrule10+privacyrule11+privacyrule12+privacyrule13) != 0:
			result = result + ',' + "(privacy leak)"

		# 4、browser
		browserrule1 = is_sort(2, s2, ["更改"], ["设置"])
		browserrule2 = is_sort(4, s2, ["更改"], ["历史"])
		if (browserrule1 + browserrule2) != 0:
			result = result + ',' + "(browser)"

		# 5、bad performance
		badpfrule1 = is_in_sentence(sen2, ["死机", "卡机", "费电", "耗电"])
		badpfrule2 = is_sort(3, s2, ["CPU"], ["降"])
		badpfrule3 = is_sort(3, s2, ["CPU"], ["高"])
		badpfrule4 = is_sort(3, s2, ["拔"], ["电池"])
		badpfrule5 = is_sort(3, s2, ["扣"], ["电池"])

		if (badpfrule1+badpfrule2+badpfrule3+badpfrule4+badpfrule5) != 0:
			result = result + ',' + "(bad performance)"
		
		# 6、payment
		paymentrule1 = is_sort(13, s2, ["自动"], ["扣"])
            	paymentrule2 = is_sort(10, s2, ["扣"], ["话费"])
            	paymentrule3 = is_sort(13, s2, ["扣"], ["元"])
            	paymentrule4 = is_sort(18, s2, ["扣"], ["钱"])
            	paymentrule5 = is_sort(9, s2, ["扣"], ["块钱"])
            	paymentrule6 = is_sort(2, s2, ["扣"], ["金币"])
            	paymentrule7 = is_sort(11, s2, ["扣"], ["块"])
            	paymentrule8 = is_sort(14, s2, ["坑"], ["话费"])
            	paymentrule9 = is_sort(16, s2, ["坑"], ["元"])
            	paymentrule10 = is_sort(19, s2, ["坑"], ["钱"])
            	paymentrule11 = is_sort(11, s2, ["坑"], ["块钱"])
            	paymentrule12 = is_sort(6, s2, ["坑"], ["金币"])
            	paymentrule13 = is_sort(14, s2, ["坑"], ["块"])
            	paymentrule14 = is_sort(4, s2, ["被扣"], ["话费"])
            	paymentrule15 = is_sort(8, s2, ["被扣"], ["元"])
            	paymentrule16 = is_sort(7, s2, ["被扣"], ["钱"])
            	paymentrule17 = is_sort(3, s2, ["被扣"], ["块钱"])
            	paymentrule18 = is_sort(3, s2, ["被扣"], ["块"])
            	paymentrule19 = is_sort(12, s2, ["骗"], ["话费"])
            	paymentrule20 = is_sort(19, s2, ["骗"], ["元"])
            	paymentrule21 = is_sort(15, s2, ["骗"], ["钱"])
            	paymentrule22 = is_sort(10, s2, ["骗"], ["块钱"])
            	paymentrule23 = is_sort(10, s2, ["骗"], ["金币"])
            	paymentrule24 = is_sort(10, s2, ["骗"], ["块"])
		if (paymentrule1+paymentrule2+paymentrule3+paymentrule4+paymentrule5+paymentrule6+paymentrule7+paymentrule8+paymentrule9+paymentrule10+paymentrule11+paymentrule12
		   +paymentrule13+paymentrule14+paymentrule15+paymentrule16+paymentrule17+paymentrule18+paymentrule19+paymentrule20+paymentrule21+paymentrule22+paymentrule23+paymentrule24) != 0:
			result = result + ',' + "(payment)"

		# 7、network traffic
		networkrule1 = is_sort(4, s2, ["偷"], ["流量"])
		networkrule2 = is_sort(8, s2, ["骗"], ["流量"])
		if (networkrule1+networkrule2) != 0:
			result = result + ',' + "(network traffic)"


		# 8、drive-by download
		driverule1 = is_sort(1, s2, ["自动"], ["下"])
            	driverule2 = is_sort(5, s2, ["捆绑"], ["下载"])
            	driverule3 = is_sort(6, s2, ["捆绑"], ["安装"])
            	driverule4 = is_sort(12, s2, ["捆绑"], ["下"])
            	driverule5 = is_sort(6, s2, ["捆绑"], ["安"])
            	driverule6 = is_sort(4, s2, ["强制"], ["下载"])
            	driverule7 = is_sort(1, s2, ["强制"], ["安装"])
            	driverule8 = is_sort(4, s2, ["强制"], ["下"])
            	driverule9 = is_sort(1, s2, ["强制"], ["安"])
            	driverule10 = is_sort(2, s2, ["下载"], ["其他"])
            	driverule11 = is_sort(3, s2, ["安装"], ["其他"])
            	driverule12 = is_sort(2, s2, ["下"], ["其他"])
            	driverule13 = is_sort(3, s2, ["安"], ["其他"])
            	driverule14 = is_sort(4, s2, ["后台"], ["下载"])
            	driverule15 = is_sort(2, s2, ["后台"], ["安装"])
            	driverule16 = is_sort(4, s2, ["后台"], ["下"])
            	driverule17 = is_sort(2, s2, ["后台"], ["安"])
            	driverule18 = is_sort(1, s2, ["绑定"], ["下载"])
            	driverule19 = is_sort(1, s2, ["绑定"], ["下"])
		if (driverule1+driverule2+driverule3+driverule4+driverule5+driverule6+driverule7+driverule8+driverule9+driverule10+driverule11+driverule12+driverule13
		   +driverule14+driverule15+driverule16+driverule17+driverule18+driverule19) != 0:
			result = result + ',' + "(drive-by download)"


		# 9、hidden app
		hiddenrule1 = is_sort(2, s2, ["图标"], ["隐藏"])
		hiddenrule2 = is_sort(2, s2, ["图标"], ["消失"])
		hiddenrule3 = is_sort(2, s2, ["图标"], ["找不到"])
		if (hiddenrule1+hiddenrule2+hiddenrule3) != 0:
			result = result + ',' + "(hidden app)"
		

		# 10、fail to uninstall
		uninstallrule1 = is_sort(4, s2, ["不能"], ["卸载"])
            	uninstallrule2 = is_sort(5, s2, ["怎么"], ["卸载"])
            	uninstallrule3 = is_sort(1, s2, ["无法"], ["卸载"])
            	uninstallrule4 = is_sort(3, s2, ["卸载"], ["不"])
            	uninstallrule5 = is_sort(2, s2, ["不能"], ["卸"])
            	uninstallrule6 = is_sort(3, s2, ["怎么"], ["卸"])
            	uninstallrule7 = is_sort(1, s2, ["无法"], ["卸"])
            	uninstallrule8 = is_sort(4, s2, ["卸"], ["不"])
            	uninstallrule9 = is_sort(4, s2, ["不能"], ["删"])
            	uninstallrule10 = is_sort(1, s2, ["怎么"], ["删"])
            	uninstallrule11 = is_sort(1, s2, ["无法"], ["删"])
            	uninstallrule12 = is_sort(2, s2, ["删"], ["不"])
            	uninstallrule13 = is_sort(2, s2, ["删"], ["不"])
            	uninstallrule14 = is_sort(3, s2, ["隐藏"], ["自己"])
            	uninstallrule15 = is_sort(1, s2, ["自己"], ["隐藏"])
		if (uninstallrule1+uninstallrule2+uninstallrule3+uninstallrule4+uninstallrule5+uninstallrule6+uninstallrule7+uninstallrule8+uninstallrule9+uninstallrule10
		   +uninstallrule11+uninstallrule12+uninstallrule13+uninstallrule14+uninstallrule15) != 0:
			result = result + ',' + "(fail to uninstall)"

		# 11、powerboot
		powerbootrule1 = is_sort(1, s2, ["开机"], ["自启"])
            	powerbootrule2 = is_sort(6, s2, ["开机"], ["启动"])
		if (powerbootrule1+powerbootrule2) ！=0:
			result = result + ',' + "(powerboot)"

		# 12、fail to start
		startrule1 = is_in_sentence(sen2, ["闪退", "打不开", "进不去", "崩溃"])
            	startrule2 = is_sort(1, s2, ["运行"], ["不了"])
            	startrule3 = is_sort(1, s2, ["停止"], ["运行"])
            	startrule4 = is_sort(1, s2, ["自动"], ["停止"])
            	startrule5 = is_sort(1, s2, ["自动"], ["退出"])
		if (startrule1+startrule2+startrule3+startrule4+startrule5) != 0:
			result = result + ',' + "(fail to start)"

		# 13、fail to exit
		exitrule1 = is_sort(1, s2, ["退"], ["不出"])
		exitrule2 = is_sort(1, s2, ["退"], ["不了"])
		exitrule3 = is_sort(2, s2, ["不能"], ["退出"])
		exitrule4 = is_sort(2, s2, ["无法"], ["退出"])
		exitrule5 = is_sort(2, s2, ["怎么"], ["退出"])
		exitrule6 = is_sort(2, s2, ["不让"], ["退出"])
		exitrule7 = is_sort(3, s2, ["后台"], ["运行"])
		if (exitrule1+exitrule2+exitrule3+exitrule4+exitrule5+exitrule6+exitrule7) != 0:
			result = result + ',' + "(fail to exit)"

		# 14、 retrieve content
		contentrule1 = is_in_sentence(sen2, ["空白"])
            	contentrule2 = is_sort(2, s2, ["数据"], ["不了"])
            	contentrule3 = is_sort(2, s2, ["不了"], ["数据"])
		if (contentrule1+contentrule2+contentrule3) != 0:
			result = result + ',' + "(retrieve content)"

		# 15、notification ad
		notifirule1 = is_sort(4, s2, ["通知栏"], ["广告"])
            	notifirule2 = is_sort(4, s2, ["通知栏"], ["不掉"])
		notifirule2 = is_sort(4, s2, ["通知栏"], ["收不到"])
		if (notifirule1+notifirule2) != 0:
			result = result + ',' + "(notification ad)"

		# 16、fail to login
		loginrule1 = is_sort(6, s2, ["验证码"], ["不"])
            	loginrule2 = is_sort(3, s2, ["验证码"], ["不了"])
            	loginrule3 = is_sort(1, s2, ["登录"], ["不上"])
            	loginrule4 = is_sort(3, s2, ["不能"], ["登录"])
            	loginrule5 = is_sort(3, s2, ["登录"], ["不"])
            	loginrule6 = is_sort(1, s2, ["登录"], ["不了"])
            	loginrule7 = is_sort(1, s2, ["登陆"], ["不上"])
            	loginrule8 = is_sort(3, s2, ["不能"], ["登陆"])
            	loginrule9 = is_sort(4, s2, ["登陆"], ["不"])
            	loginrule10 = is_sort(3, s2, ["登陆"], ["不了"])
            	loginrule11 = is_sort(1, s2, ["注册"], ["不上"])
            	loginrule12 = is_sort(1, s2, ["不能"], ["注册"])
            	loginrule13 = is_sort(3, s2, ["注册"], ["不"])
            	loginrule14 = is_sort(3, s2, ["注册"], ["不了"])
		if (loginrule1+loginrule2+loginrule3+loginrule4+loginrule5+loginrule6+loginrule7+loginrule8+loginrule9+loginrule10+loginrule11+loginrule12+loginrule13+loginrule14) != 0:
			result = result + ',' + "(fail to login)"

		# 17、add shortcuts
		shortcutrule1 = is_in_sentence(sen2, ["桌面"])
            	shortcutrule2 = is_in_sentence(sen2, ["广告"])
		if (shortcutrule1+shortcutrule2) != 0:
			result = result + ',' + "(add shortcuts)"

		# 18、fail to install
		installrule1 = is_sort(2, s2, ["不能"], ["安装"])
            	installrule2 = is_sort(1, s2, ["安装"], ["失败"])
            	installrule3 = is_sort(2, s2, ["怎么"], ["安装"])
            	installrule4 = is_sort(1, s2, ["安装"], ["不上"])
            	installrule5 = is_sort(2, s2, ["不能"], ["安"])
            	installrule6 = is_sort(1, s2, ["安"], ["失败"])
            	installrule7 = is_sort(2, s2, ["不能"], ["安"])
            	installrule8 = is_sort(1, s2, ["安"], ["不上"])
		if (installrule1+installrule2+installrule3+installrule4+installrule5+installrule6+installrule7+installrule8) != 0:
			result = result + ',' + "(fail to install)"

		# 19、redirection
		redirectrule1 = is_sort(7, s2, ["要"], ["激活"])
            	redirectrule2 = is_sort(5, s2, ["其他"], ["激活"])
            	redirectrule3 = is_sort(8, s2, ["下"], ["激活"])
            	redirectrule4 = is_sort(8, s2, ["下载"], ["激活"])
            	redirectrule5 = is_sort(10, s2, ["安装"], ["激活"])
		if (redirectrule1+redirectrule2+redirectrule3+redirectrule4+redirectrule5) != 0:
			result = result + ',' + "(redirection)"

		# 20、vulgar content
		vulgarrule1 = is_in_sentence(sen2, ["黄色", "血腥", "暴力"])
		if vulgarrule1 != 0:
			result = result + ',' + "(vulgar content)"

		# 21、inconsistency
		inconsistrule1 = is_sort(7, s2, ["图片"], ["不一样"])
		inconsistrule2 = is_sort(7, s2, ["介绍"], ["不一样"])
		inconsistrule3 = is_sort(7, s2, ["封面"], ["不一样"])
		if (inconsistrule1+inconsistrule2+inconsistrule3) != 0:
			result = result + ',' + "(inconsistency)"

		# 22、background
		backgroundrule1 = is_sort(3, s2, ["自动"], ["下载"])
            	backgroundrule2 = is_sort(2, s2, ["自动"], ["安装"])
            	backgroundrule3 = is_sort(3, s2, ["自动"], ["下"])
            	backgroundrule4 = is_sort(4, s2, ["自动"], ["安"])
            	backgroundrule5 = is_sort(2, s2, ["自动"], ["发短信"])
            	backgroundrule6 = is_sort(3, s2, ["自己"], ["下载"])
            	backgroundrule7 = is_sort(2, s2, ["自己"], ["安装"])
            	backgroundrule8 = is_sort(3, s2, ["自己"], ["下"])
            	backgroundrule9 = is_sort(2, s2, ["自己"], ["安"])
            	backgroundrule10 = is_sort(1, s2, ["自己"], ["发短信"])
            	backgroundrule11 = is_sort(4, s2, ["强制"], ["下载"])
            	backgroundrule12 = is_sort(1, s2, ["强制"], ["安装"])
            	backgroundrule13 = is_sort(3, s2, ["强制"], ["下"])
            	backgroundrule14 = is_sort(1, s2, ["强制"], ["安"])
            	backgroundrule15 = is_sort(4, s2, ["一直"], ["下载"])
            	backgroundrule16 = is_sort(3, s2, ["一直"], ["安装"])
            	backgroundrule17 = is_sort(4, s2, ["一直"], ["下"])
            	backgroundrule18 = is_sort(2, s2, ["一直"], ["安"])
            	backgroundrule19 = is_sort(3, s2, ["不停"], ["下载"])
            	backgroundrule20 = is_sort(3, s2, ["不停"], ["安装"])
            	backgroundrule21 = is_sort(3, s2, ["不停"], ["下"])
            	backgroundrule22 = is_sort(3, s2, ["不停"], ["安"])
            	backgroundrule23 = is_sort(3, s2, ["不停"], ["发短信"])
            	backgroundrule24 = is_sort(3, s2, ["后台"], ["下载"])
            	backgroundrule25 = is_sort(3, s2, ["后台"], ["下载"])
            	backgroundrule26 = is_sort(3, s2, ["后台"], ["下"])
            	backgroundrule27 = is_sort(3, s2, ["后台"], ["安"])
            	backgroundrule28 = is_sort(3, s2, ["后台"], ["发短信"])
		if (backgroundrule1+backgroundrule2+backgroundrule3+backgroundrule4+backgroundrule5+backgroundrule6+backgroundrule7+backgroundrule8+backgroundrule9
		   +backgroundrule10+backgroundrule11+backgroundrule12+backgroundrule13+backgroundrule14+backgroundrule15+backgroundrule16+backgroundrule17+backgroundrule18
		   +backgroundrule19+backgroundrule20+backgroundrule21+backgroundrule22+backgroundrule23+backgroundrule24+backgroundrule25+backgroundrule26+backgroundrule27
		   +backgroundrule28) != 0:
			result = result + ',' + "(background)"

		# 23、permission abuse
		premisisonrule1 = is_sort(5, s2, ["要"], ["权限"])
		if premisisonrule1 == 1:
			result = result + ',' + "(permission abuse)"

		# 24、update
		updaterule1 = is_sort(4, s2, ["更新"], ["其他"])
		if updaterule1 == 1:
			result = result + ',' + "(update)"

		# 25、repackage
		repackagerule1 = is_in_sentence(sen2, ["盗版", "破解版"])
		if repackagerule1 == 1:
			result = result + ',' + "(repackage)"
			
		# 26、ranking fraud
		behavior260 = is_sort(3, s2, ["评论"], ["假"])
		behavior260 = is_sort(4, s2, ["评论"], ["刷"])
		behavior260 = is_sort(3, s2, ["好评"], ["假"])
		behavior260 = is_sort(5, s2, ["好评"], ["刷"])
		behavior261 = is_sort(2, s2, ["刷"], ["评论"])
		behavior261 = is_sort(2, s2, ["刷"], ["好评"])
		behavior261 = is_sort(2, s2, ["假"], ["评论"])
		behavior261 = is_sort(2, s2, ["假"], ["好评"])
		if (behavior260+behavior261) != 0:
			result = result + ',' + "(ranking fraud)"
			
			
		print(result)
   

if __name__ == '__main__':
    detect('评论内容 ')
