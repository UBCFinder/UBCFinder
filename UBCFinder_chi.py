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
            if myword in words:
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
		behavior1 = is_in_sentence(sen2, ["广告"])
		behavior11 = is_sort(7, s2, ["没", "避免", "去", "看", "无"], ["广告"])
		behavior12 = is_sort(7, s2, ["广告"], ["没", "少", "不多"])
		if behavior1 == 1 and "桌面" not in sen2 and "通知栏" not in sen2 and behavior11 != 1 and behavior12 != 1:
			result = result + ',' + "(ad disruption)"

		# 2、virus
		behavior21 = is_in_sentence(sen2, ["病毒", "木马"])
		behavior22 = is_in_list(s2, ["毒"])
		behavior23 = is_in_list(s2, ["有", "查"])
		behavior24 = is_sort(4, s2, ["没"], ["毒", "木马"])
		if behavior21 == 1 and behavior24 != 1:
			result = result + ',' + "(virus)"
		elif behavior22 == 1 and behavior23 == 1 and behavior24 != 1:
			result = result + ',' + "(virus)"

		# 3、privacy leak
		behavior31 = is_in_sentence(sen2, ["盗"])
		behavior32 = is_in_sentence(sen2, ["信息"])
		behavior33 = is_sort(3, s2, ["盗"], ["信息"])
		behavior34 = is_in_sentence(sen2, ["资料", "照片", "文件", "数据", "备份", "相册"])
		behavior35 = is_in_sentence(sen2, ["没了", "没有了", "不见了"])
		behavior36 = is_sort(8, s2, ["资料", "照片", "文件", "数据", "备份", "相册"], ["没", "不见"])
		if behavior31 == 1 and behavior32 == 1 and behavior33 == 1:
			result = result + ',' + "(privacy leak)"
		elif behavior34 == 1 and behavior35 == 1 and behavior36 == 1:
			result = result + ',' + "(privacy leak)"

		# 4、browser
		behavior41 = is_in_sentence(sen2, ["浏览器"])
		behavior42 = is_sort(4, s2, ["更改"], ["设置"])
		if behavior41 == 1 and behavior42 == 1:
			result = result + ',' + "(browser)"

		# 5、bad performance
		behavior51 = is_in_sentence(sen2, ["死机", "卡机"])
		behavior52 = is_sort(4, s2, ["手机","电话"], ["卡"])
		behavior53 = is_sort(4, s2, ["不","绑"], ["卡"])
		behavior54 = is_in_sentence(sen2, ["信号"])
		behavior55 = is_similar(s2, ["差"])
		behavior56 = is_in_sentence(sen2, ["系统崩溃", "自动关机"])
		behavior57 = is_in_sentence(sen2, ["CPU", "占用", "高"])
		behavior58 = is_sort(5, s2, ["CPU"], ["占用", "高"])
		behavior59 = is_in_sentence(sen2, ["耗电", "电池", "发热", "费电", "没电", "发烫"])

		if behavior51 == 1 and behavior53 != 1:
			result = result + ',' + "(bad performance)"
		elif behavior52 == 1 and behavior53 != 1:
			result = result + ',' + "(bad performance)"
		elif behavior54 == 1 and behavior55 == 1:
			result = result + ',' + "(bad performance)"
		elif behavior56 == 1:
			result = result + ',' + "(bad performance)"
		elif behavior57 == 1 and behavior58 == 1:
			result = result + ',' + "(bad performance)"
		elif behavior59 == 1 and "取电池" not in sen2 and "拔电池" not in sen2 and "扣电池" not in sen2:
			result = result + ',' + "(bad performance)"

		# 6、payment
		behavior61 = is_sort(4, s2, ["扣", "骗", "坑"], ["话费", "钱", "元", "块", "币"])
		behavior62 = is_sort(4, s2, ["话费", "钱", "元", "块", "币"], ["扣", "骗", "坑"])
		behavior63 = is_in_sentence(sen2, ["短信"])
		behavior64 = is_in_sentence(sen2, ["订", "偷"])
		behavior65 = is_in_sentence(sen2, ["自动"])
		behavior66 = is_in_sentence(sen2, ["扣", "订"])
		behavior67 = is_in_sentence(sen2, ["扣费"])
		if behavior61 == 1 or behavior62 == 1:
			result = result + ',' + "(payment)"
		elif behavior63 == 1 and behavior64 == 1:
			result = result + ',' + "(payment)"
		elif behavior65 == 1 and behavior66 == 1:
			result = result + ',' + "(payment)"
		elif behavior67 == 1:
			result = result + ',' + "(payment)"

		# 7、network traffic
		behavior71 = is_in_sentence(sen2, ["流量"])
		behavior72 = is_similar(s2, ["偷"])
		behavior73 = is_in_sentence(sen2, ["偷"])
		if behavior71 == 1 and behavior72 == 1:
			result = result + ',' + "(network traffic)"
		elif behavior71 == 1 and behavior73 == 1:
			result = result + ',' + "(network traffic)"

		# 8、drive-by download
		behavior81 = is_in_sentence(sen2, ["下", "安"])
		behavior82 = is_in_sentence(sen2, ["强迫", "强制"])
		behavior83 = is_sort(4, s2, ["强迫", "强制"], ["下", "安", "下载", "安装"])
		behavior84 = is_in_sentence(sen2, ["绑", "软件", "应用", "安装", "安装", "下载", "插件"])
		behavior85 = is_sort(5, s2, ["绑"], ["软件", "应用", "安装", "安装", "下载", "插件"])
		if behavior81 == 1 and behavior82 == 1 and behavior83 == 1:
			result = result + ',' + "(drive-by download)"
		elif behavior84 == 1 and behavior85 == 1:
			result = result + ',' + "(drive-by download)"

		# 9、hidden app
		behavior91 = is_in_sentence(sen2, ["图标"])
		behavior92 = is_in_sentence(sen2, ["隐藏", "消失", "找不到"])
		if behavior91 == 1 and behavior92 == 1:
			result = result + ',' + "(hidden app)"
		

		# 10、fail to uninstall
		behavior100_list = ["无法卸", "不能卸", "卸不了", "卸载不了", "卸不掉", "卸载不掉", "卸载失败", "不可以卸", "无法删", "不能删", "删不了", "删除不了",
					 "删不掉", "删除不掉", "删除失败", "不可以删", "卸载都不可以", "卸载都不能", "怎么卸载", "不让卸载"]
		for behavior100 in behavior100_list:
			if behavior100 in sen2:
				result = result + ',' + "(fail to uninstall)"
				break

		# 11、powerboot
		behavior110 = is_in_sentence(sen2, ["开机", "自启", "自动启", "自起"])
		behavior111 = is_sort(2, s2, ["开机"], ["自启", "自动启", "自起"])
		if behavior110 == 1 and behavior111 == 1:
			result = result + ',' + "(powerboot)"

		# 12、fail to start
		behavior120 = is_in_sentence(sen2, ["闪退", "打不开", "停止运行", "崩溃", "黑屏"])
		behavior121 = is_in_sentence(sen2, ["自动", "就", "总是", "强制", "强", "强行", "异常", "退", "退出"])
		behavior122 = is_sort(2, s2, ["自动", "就", "总是", "强制", "强", "强行", "异常"], ["退", "退出"])
		behavior123 = is_in_sentence(sen2, ["启动", "运行", "不了", "不能", "无法"])
		behavior124 = is_sort(5, s2, ["启动", "运行"], ["不了"])
		behavior125 = is_sort(5, s2, ["不能", "无法"], ["启动", "运行"])
		behavior126 = is_sort(7, s2, ["不会", "很少", "没", "没有"], ["闪退", "打不开", "停止运行", "崩溃", "黑屏"])
		if behavior120 == 1 and behavior126 != 1:
			result = result + ',' + "(fail to start)"
		elif behavior121 == 1 and behavior122 == 1:
			result = result + ',' + "(fail to start)"
		elif behavior123 == 1 and behavior124 == 1:
			result = result + ',' + "(fail to start)"
		elif behavior123 == 1 and behavior125 == 1:
			result = result + ',' + "(fail to start)"

		# 13、fail to exit
		behavior130 = is_in_sentence(sen2, ["退", "不出", "不了"])
		behavior131 = is_sort(1, s2, ["退"], ["不出", "不了"])
		behavior132 = is_in_sentence(sen2, ["不能", "无法", "怎么", "不让", "没办法", "退出"])
		behavior133 = is_sort(2, s2, ["不能", "无法", "怎么", "不让", "没办法"], ["退出"])
		behavior134 = is_in_sentence(sen2, ["后台", "运行"])
		behavior135 = is_sort(3, s2, ["后台"], ["运行"])
		if behavior130 == 1 and behavior131 == 1:
			result = result + ',' + "(fail to exit)"
		elif behavior132 == 1 and behavior133 == 1:
			result = result + ',' + "(fail to exit)"
		elif behavior134 == 1 and behavior135 == 1:
			result = result + ',' + "(fail to exit)"

		# 14、 retrieve content
		behavior140 = is_in_sentence(sen2, ["获取不了数据", "获取不到数据", "空白"])
		behavior141 = is_sort(3, se, ["内容"], ["空白"])
		if behavior140 == 1 or behavior141 == 1:
			result = result + ',' + "(retrieve content)"

		# 15、notification ad
		behavior150 = is_in_sentence(sen2, ["通知栏"])
		behavior151 = is_in_sentence(sen2, ["不能", "不可以", "不显示", "广告", "收不到", "显示不出来", "设置不了", "弄不掉"])
		behavior152 = is_sort(5, s2, ["不", "没有"], ["通知"])
		if behavior150 == 1 and behavior151 == 1 and behavior152 != 1:
			result = result + ',' + "(notification ad)"

		# 16、fail to login
		behavior160 = is_in_sentence(sen2, ["验证码"])
		behavior161 = is_in_sentence(sen2, ["不"])
		behavior162 = is_sort(3, s2, ["登", "注册"], ["不了", "不行", "失败"])
		behavior163 = is_sort(3, s2, ["无法", "没法", "没办法", "不能"], ["登", "注册"])
		if behavior160 == 1 and behavior161 == 1:
			result = result + ',' + "(fail to login)"
		elif behavior162 == 1 or behavior163 == 1:
			result = result + ',' + "(fail to login)"

		# 17、add shortcuts
		behavior170 = is_in_sentence(sen2, ["桌面"])
		behavior171 = is_in_sentence(sen2, ["广告"])
		if behavior170 == 1 and behavior171 == 1:
			result = result + ',' + "(add shortcuts)"

		# 18、fail to install
		behavior180 = is_sort(3, s2, ["安", "安装"], ["不", "失败"])
		behavior181 = is_sort(3, s2, ["无法", "不能", "不让"], ["安装", "安"])
		behavior182 = is_sort(3, s2, ["安全", "安静", "安排", "安卓"], ["不", "失败"])
		behavior183 = is_sort(3, s2, ["安"], ["不知道", "不会"])
		behavior184 = is_sort(3, s2, ["无法", "不能", "不让"], ["安全", "安静", "安卓"])
		if behavior180 == 1 and behavior182 != 1 and behavior183 != 1:
			result = result + ',' + "(fail to install)"
		elif behavior181 == 1 and behavior184 != 1:
			result = result + ',' + "(fail to install)"

		# 19、redirection
		behavior190 = is_sort(5, s2, ["安", "下"], ["才能","才让","才可以"])
		behavior191 = is_in_sentence(sen2, ["激活"])
		behavior192 = is_in_sentence(sen2, ["另一个", "再下", "下载", "其他", "别的"])
		behavior193 = is_sort(5, s2, ["一下", "安卓"], ["才能","才让","才可以"])
		behavior194 = is_sort(5, s2, ["才能","才让","才可以"], ["玩", "用", "打开"])
		behavior195 = is_sort(5, s2, ["不用"], ["安", "下"])
		if behavior190 == 1 and behavior193 != 1 and behavior194 != 1 and behavior195 != 1:
			result = result + ',' + "(redirection)"
		elif behavior191 == 1 and behavior192 == 1:
			result = result + ',' + "(redirection)"

		# 20、vulgar content
		behavior200 = is_in_sentence(sen2, ["黄色", "血腥", "暴力", "反社会", "反党", "邪教", "法轮功"])
		behavior201 = is_in_sentence(sen2, ["催收", "威胁", "拒绝暴力", "无暴力"])
		if behavior200 == 1 and behavior201 != 1:
			result = result + ',' + "(vulgar content)"

		# 21、inconsistency
		behavior210 = is_sort(10, s2, ["图片", "介绍", "图案", "封面"], ["不一致", "不一样"])
		if behavior210 == 1:
			result = result + ',' + "(inconsistency)"

		# 22、background
		behavior220 = is_sort(4, s2, ["自动", "自己", "后台", "偷", "一直", "不停", "强制", "强行"], ["下", "安", "发短信", "备份"])
		behavior221 = is_sort(4, s2, ["一直"], ["使用", "下去", "下来", "安卓", "安全", "走"])
		behavior222 = is_sort(4, s2, ["自己"], ["下去", "下来", "试了下", "下了", "上下", "下一个", "安排", "安全", "一下", "也", "下单"])
		if behavior220 == 1 and behavior221 != 1 and behavior222 != 1:
			result = result + ',' + "(background)"

		# 23、permission abuse
		behavior230 = is_sort(5, s2, ["强行", "一直", "要"], ["权限"])
		behavior231 = is_sort(5, s2, ["权限"], ["问题", "多"])
		if behavior230 == 1 or behavior231 == 1:
			result = result + ',' + "(permission abuse)"

		# 24、update
		behavior240 = is_sort(4, s2, ["更新"], ["其他"])
		behavior241 = is_in_sentence(sen2, ["更新其他"])
		behavior242 = is_sort(3, s2, ["更新"], ["比", "还行"])
		if behavior240 == 1 and behavior241 != 1 and behavior242 != 1:
			result = result + ',' + "(update)"

		# 25、repackage
		behavior250 = is_in_sentence(sen2, ["盗版", "破解版"])
		if behavior250 == 1:
			result = result + ',' + "(repackage)"
			
		# 26、ranking fraud
		behavior260 = is_sort(3, s2, ["评论", "好评"], ["刷", "假"])
		behavior261 = is_sort(3, s2, ["刷", "假"], ["评论", "好评"])
		if behavior260 or behavior261 == 1:
			result = result + ',' + "(ranking fraud)"
			
			
		print(result)
   

if __name__ == '__main__':
    detect('评论内容 ')
