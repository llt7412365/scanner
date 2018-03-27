# coding:utf-8
import sys
import time
import copy
import log
import scripts.s123
import scripts.s142
import scripts.s145
import scripts.s146
import scripts.s186
import scripts.s775
import scripts.s1169
from MySqlConn import Mysql
from scripts import *


class ScanMaster(object):

    def __init__(self):
        self.mysql = Mysql()

    def logs(self):
        info = sys.exc_info()
        level = 4
        lylog = log.LogMaster('scan_log', info, level)
        lylog.buildLog()

    def identify(self, port, protocol, banner):
        vul_list = []
        sql = "select id,port,state from sys_vul"
        info = self.mysql.getAll(sql)
        for msg in info:
            if msg['state']:
                port_list = msg['port'].split(',')
                for p in port_list:
                    if str(port) == p:
                        vul_list.append(msg['id'])
        return vul_list

    def choose(self, port, vul_plug_id):
        vul_list = []
        sql = "select port from sys_vul where id=%s and state=1"
        vid_list = vul_plug_id.split(',')
        for i in vid_list:
            result = self.mysql.getOne(sql, (i))
            data = result['port']
            port_list = str(data).split(',')
            if str(port) in port_list:
                vul_list.append(i)
        return vul_list

    def door(self, t_id, vul_plug_id, ip, port, protocol, banner, content):
        url = ''
        state = {}
        data = ''
        vid_list = []
        if vul_plug_id == '0':
            try:
                vid_list = self.identify(port, protocol, banner)
            except Exception:
                self.logs()
        else:
            try:
                vid_list = self.choose(port, vul_plug_id)
            except Exception:
                self.logs()
        for i in vid_list:
            s_name = 's' + str(i)
            if s_name == 's1168':
                if content and 'hikvision' not in content.lower():
                    continue
            result = eval(s_name).start(ip, port, protocol)
            if result:
                state, url, data = result
            if state:
                self.insert_vullist(ip, port, url, i, data, t_id)
            else:
                self.updete_vullist(ip, port, i, t_id)

    def find_count(self, ip, port, vul_id):
        sql1 = "select * from tbl_vullist where IP=%s and port=%s and vul_id=%s"
        sql2 = "select vul_name,grade from sys_vul where id=%s"
        result = self.mysql.getOne(sql2, (vul_id))
        grade = result['grade']
        vul_name = result['vul_name']
        data_count = self.mysql.getCount(sql1, (ip, port, vul_id))
        result2 = self.mysql.getOne(sql1, (ip, port, vul_id))
        vullist_id = None
        if result2:
            vullist_id = result2['id']
        return int(data_count), vullist_id, vul_name, grade

    def change(self, ip):
        ip_list = ip.split('.')
        ip_list1 = copy.copy(ip_list)
        for i in ip_list:
            if len(i) == 2:
                ip_list1[ip_list1.index(i)] = '0' + i
            elif len(i) == 1:
                ip_list1[ip_list1.index(i)] = '00' + i
        return int(''.join(ip_list1))

    def find_area_id(self, ip):
        try:
            sql = 'select area_id,IP_location from sys_ip_location where inet_aton(IP_start) <= inet_aton(%s) AND inet_aton(IP_end)>=inet_aton(%s);'
            result = self.mysql.getOne(sql, (ip, ip))
            area_id = result['area_id']
            ip_location = result['IP_location']
            return area_id, ip_location
        except Exception:
            try:
                country, province, city, operator = location.find_location(ip)
                if country and province:
                    sql2 = 'select code from sys_administrative_area where name=%s or name=%s'
                    result = self.mysql.getOne(sql2, (city, province))
                    code = result['code']
                    ip_location2 = province + city
                    sql3 = "insert into sys_ip_location (IP_start,IP_end,IP_loc_county,IP_loc_province,IP_loc_city,IP_loc_district,operator,area_id,IP_location,aton_start,aton_end) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,inet_aton(%s),inet_aton(%s))"
                    self.mysql.insertOne(
                        sql3, (ip, ip, country, province, city, '', operator, code, ip_location2, ip, ip))
                    return code, ip_location2
            except Exception:
                return '', ''

    def insert_vullist(self, ip, port, url, vul_id, detail, t_id):
        count, vullist_id, vul_name, grade = self.find_count(ip, port, vul_id)
        now_time = time.strftime('%Y-%m-%d %H-%M-%S')
        if count:
            sql = "update tbl_vullist set update_time=%s,is_repair=%s,is_newly_added=%s where IP=%s and port=%s and vul_id=%s"
            self.mysql.update(sql, (now_time, 0, 1, ip, port, vul_id))
        else:
            print '---->', ip
            area_id, IP_location = self.find_area_id(ip)
            sql = "insert into tbl_vullist (IP,port,url,vul_id,add_time,detail,vul_name,grade,t_id,area_id,IP_location) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            vullist_id = self.mysql.insertOne(sql, (ip, port, url, vul_id, now_time, detail, vul_name, grade, t_id, area_id, IP_location))
        self.count_vul(t_id, vullist_id, vul_id, 1)

    def updete_vullist(self, ip, port, vul_id, t_id):
        count, vullist_id, vul_name, grade = self.find_count(ip, port, vul_id)
        if count:
            now_time = time.strftime('%Y-%m-%d %H-%M-%S')
            sql = "update tbl_vullist set repair_time=%s,update_time=%s,is_repair=%s,is_newly_added=%s where IP=%s and port=%s and vul_id=%s"
            self.mysql.update(sql, (now_time, now_time, 1, 0, ip, port, vul_id))
            self.count_vul(t_id, vullist_id, vul_id, 2)

    def count_vul(self, t_id, vullist_id, vul_id, state):
        sql = "select vul_info,vul_count from tbl_task where id=%s"
        result = self.mysql.getOne(sql, (t_id))
        vul_info = result['vul_info']
        vul_count = result['vul_count']
        vul_list = vul_count.split(',')
        w_all = vul_list[0]
        w_1 = vul_list[1]
        w_2 = vul_list[2]
        w_3 = vul_list[3]
        sql2 = "select grade from tbl_vullist where id=%s"
        result = self.mysql.getOne(sql2, (vullist_id))
        grade = result['grade']
        if state == 1:
            if grade == 1:
                w_3 = str(int(w_3) + 1)
                w_all = str(int(w_all) + 1)
            elif grade == 2:
                w_2 = str(int(w_2) + 1)
                w_all = str(int(w_all) + 1)
            else:
                w_1 = str(int(w_1) + 1)
                w_all = str(int(w_all) + 1)

        insert_count = []
        insert_count.append(w_all)
        insert_count.append(w_1)
        insert_count.append(w_2)
        insert_count.append(w_3)
        new_vul_count = ','.join(insert_count)
        if state == 1:
            new_vul_info = str(vullist_id)
            if vul_info:
                new_vul_info = vul_info + ',' + str(vullist_id)

        else:
            new_vul_info = vul_info
            if vul_info:
                info_list = vul_info.split(',')
                if str(vul_id) in info_list:
                    new_vul_info = ','.join(info_list.remove(str(vul_id)))
        sql3 = "update tbl_task set vul_info=%s,vul_count=%s where id=%s"
        self.mysql.update(sql3, (new_vul_info, new_vul_count, t_id))

if __name__ == '__main__':
    pass
