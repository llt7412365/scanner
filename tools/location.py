#!/usr/local/bin/python
# coding: utf-8
import urllib2
import json
import time
import chardet

url = 'http://ip.taobao.com/service/getIpInfo.php?ip='


def find_location(ip):
    try:
        response = urllib2.urlopen(url + ip, timeout=5)
        result = response.readlines()
        data = json.loads(result[0])
        country = data['data']['country']
        province = data['data']['region']
        city = data['data']['city']
        operator = data['data']['isp']
        if country.encode('utf8') == "台湾":
            country = '中国'
        return country, province, city, operator
    except:
        return