# coding:utf-8
import os
import re
import sys
import log
import time
import requests
import location
from MySqlConn import Mysql
from crossroads import ScanMaster


class AssetDiscovery(object):

    def __init__(self):
        self.mysql = Mysql()

    def logs(self):
        info = sys.exc_info()
        level = 4
        lylog = log.LogMaster('scan_log', info, level)
        lylog.buildLog()

    def find_range_ip(self, dete_obj):
        ip_list = dete_obj.split('-')
        ip_start = ip_list[0]
        ip_end = ip_list[-1]
        sql = 'select IP,detection_times,port_info from tbl_asset where inet_aton(%s)<= inet_aton(ip) AND inet_aton(%s)>=inet_aton(ip)'
        info = self.mysql.getAll(sql, (ip_start, ip_end))
        count = self.mysql.getCount(sql)
        return count, info

    def process(self, num1, num2):
        a = float(num1)
        b = float(num2)
        sche = "%.f%%" % (b / a * 100)
        return sche

    def find_asset_count(self):
        sql = "select * from tbl_asset where state=%s"
        count = self.mysql.getCount(sql, (1))
        return int(count)

    def find_asset(self, dete_obj, content_type, vul_plug_id, t_id):
        sql1 = "select IP,detection_times,port_info from tbl_asset"
        info = self.mysql.getAll(sql1)
        count = self.mysql.getCount(sql1)
        if '-' in dete_obj:
            count, info = self.find_range_ip(dete_obj)
        if count != 0:
            for index, msg in enumerate(info, 1):
                ip = msg['IP']
                print ip
                self.scan(msg, content_type, vul_plug_id, t_id)
                proces = self.process(count, index)
                asset_count = self.find_asset_count()
                sql2 = "update tbl_task set curr_process=%s,asset_count=%s where id=%s"
                self.mysql.update(sql2, (proces, asset_count, t_id))
            now_time = time.strftime('%Y-%m-%d %H:%M:%S')
            sql3 = "update tbl_task set end_time=%s,state=%s where id=%s"
            self.mysql.update(sql3, (now_time, 2, t_id))
        else:
            now_time = time.strftime('%Y-%m-%d %H:%M:%S')
            sql4 = "update tbl_task set end_time=%s,curr_process=%s,state=%s where id=%s"
            self.mysql.update(sql4, (now_time, '100%', 2, t_id))

    def update_asset(self, host, os, items, all_port, device_type, device_info):
        area_id, IP_location = self.find_area_id(host)
        detection_times = int(items) + 1
        state = 1
        if all_port:
            state = 1
        else:
            state = 0

        update_time = time.strftime('%Y-%m-%d %H:%M:%S')
        sql = "update tbl_asset set update_time=%s,area_id=%s,IP_location=%s,state=%s,detection_times=%s,os=%s,device_type=%s, device_info=%s where IP=%s"
        self.mysql.update(sql, (update_time, area_id, IP_location,
                                state, detection_times, os, device_type, device_info, host))

    def update_port_info(self, all_port, host):
        port_info = str(all_port)
        sql = '''update tbl_asset set port_info="%s" where IP="%s"''' % (
            port_info, host)
        self.mysql.update(sql)

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

    def find_asset_id(self, ip):
        sql = 'select id,area_id from tbl_asset where IP=%s'
        result = self.mysql.getOne(sql, (ip))
        asset_id = result['id']
        area_id = result['area_id']
        return asset_id, area_id

    def find_protocol(self, port):
        sql = 'select protocol from sys_port where port=%s'
        result = self.mysql.getOne(sql, (port))
        protocol = result['protocol']
        return protocol

    def find_cate(self, cate_id):
        sql1 = 'select parent_id from sys_rule_cate where id=%s'
        sql2 = 'select cate_name from sys_rule_cate where id=%s'
        result1 = self.mysql.getOne(sql1, (cate_id))
        parent_id = result1['parent_id']
        result2 = self.mysql.getOne(sql2, (parent_id))
        cate_name = result2['cate_name']
        return cate_name

    def find_banner(self, content, title='', header=''):
        sql = "select id,rule_content,original_info,cate_id,cate_name from sys_rule"
        info = self.mysql.getAll(sql)
        id_list = []
        banner_list = []
        for msg in info:
            _id = str(msg['id'])
            rule_content = msg['rule_content']
            original_info = msg['original_info']
            cate_id = msg['cate_id']
            cate_name = msg['cate_name']
            rule = str(original_info).lower()
            if title:
                if rule in title.lower():
                    parent_cate_name = self.find_cate(cate_id)
                    id_list.append(_id)
                    banner_list.append(rule_content)
                    banner_list.append(cate_name)
                    banner_list.append(parent_cate_name)
            if content:
                if rule in content.lower():
                    parent_cate_name = self.find_cate(cate_id)
                    id_list.append(_id)
                    banner_list.append(rule_content)
                    banner_list.append(cate_name)
                    banner_list.append(parent_cate_name)
            if header:
                if rule in str(header).lower():
                    parent_cate_name = self.find_cate(cate_id)
                    id_list.append(_id)
                    banner_list.append(rule_content)
                    banner_list.append(cate_name)
                    banner_list.append(parent_cate_name)
        try:
            return ','.join(list(set(banner_list))), ','.join(list(set(id_list)))
        except Exception:
            return '', ''

    def find_manufacturer(self, content):
        if content:
            sql = 'select simple_name,keyword from sys_manufacturer'
            info = self.mysql.getAll(sql)
            for msg in info:
                simple_name = msg['simple_name']
                keyword = msg['keyword']
                key_list = []
                if ',' in keyword:
                    key_list = keyword.split(',')
                else:
                    key_list.append(keyword)
                for key in key_list:
                    if key.lower() in content.lower():
                        return simple_name
            return ''
        else:
            return ''

    def history(self, ip, dict1, dict2):
        add_time = time.strftime('%Y-%m-%d %H:%M:%S')
        if not dict1:
            dict1 = '{}'
        dict1 = eval(dict1)
        if dict1 != dict2:
            if len(dict1) > len(dict2):
                for i in dict1:
                    if i in dict2:
                        pass
                    else:
                        sql1 = "update tbl_asset_info set history=%s where IP=%s and port=%s"
                        self.mysql.update(sql1, (1, ip, i))
            else:
                for j in dict2:
                    if j in dict1:
                        pass
                    else:
                        asset_id, area_id = self.find_asset_id(ip)
                        protocol = dict2[j]
                        sql2 = "insert into tbl_asset_info (IP,port,protocol,add_time,asset_id,area_id) values(%s,%s,%s,%s,%s,%s)"
                        self.mysql.insertOne(
                            sql2, (ip, j, protocol, add_time, asset_id, area_id))


    def telnet(self, ip, port):
        cmd = 'sudo /usr/local/bin/python /var/www/html/ngscanner/scan/send.py ' + ip + ' ' + port
        output = os.popen(cmd)
        stdoutput = output.read()
        if stdoutput:
            return stdoutput.strip()
        else:
            return ''

    def send_http(self, host, port):
        protocol = self.find_protocol(port)
        if protocol == 'https':
            try:
                res = requests.get('https://' + host + ':' + str(port),
                                   timeout=5, verify=False)
                return res
            except Exception:
                return
        else:
            try:
                res = requests.get('http://' + host + ':' + str(port), timeout=5)
                return res
            except Exception:
                return

    def re_title(self, content):
        content = content.lower()
        h = re.search(r'<title>[\s\S]*?</title>', content)
        if h:
            title = h.group()
            if title:
                return title.replace('<title>', '').replace('</title>', '')

    def mod_headers(self, res):
        url = res.url
        scheme = 'HTTP'
        if url.startswith('https:'):
            scheme = 'HTTPS'
        code = res.status_code
        reason = res.reason
        h = res.headers
        he = dict(h)
        data = []
        data.append(scheme + '/' + str(code) + ' ' + reason + '\n')
        for i in h:
            data.append(i + ':' + h[i] + '\n')
        header = ''.join(data).strip()
        server = ''
        if 'Server' in he:
            server = he['Server']
        return header, server

    def mod_protocol(self, port, protocol):
        sql1 = 'select protocol from sys_port where port=%s and data_source IN (3,1) order by id desc'
        sql2 = 'select protocol from sys_port where port=%s and data_source=%s'
        sql3 = "insert into sys_port (port,protocol,data_source,cate,add_time) values(%s,%s,%s,%s,%s)"
        result = self.mysql.getOne(sql1, (port))
        db_protocol1 = result['protocol']
        if db_protocol1:
            return db_protocol1
        else:
            result2 = self.mysql.getOne(sql2, (port, 2))
            db_protocol2 = result2['protocol']
            if db_protocol2:
                return db_protocol2
            else:
                if protocol.lower() != 'unknown':
                    add_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.mysql.insertOne(sql3, (port, protocol, 2, 0, add_time))
                return protocol


    def decode(self, req):
        encoding = req.encoding
        if encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(req.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = req.apparent_encoding
        encode_content = req.content.decode(
            encoding, 'replace').encode('utf-8', 'replace')
        return encode_content

    def scan(self, data_one, content_type, vul_plug_id, t_id):
        host = data_one['IP']
        items = data_one['detection_times']
        port_info = data_one['port_info']
        OS = ''
        all_port = {}
        device_type = ''
        device_info = ''
        try:
            all_port, OS, device_type, device_info = self.nmap_scan(host)
        except Exception:
            self.logs()
        self.update_asset(host, OS, items, all_port, device_type, device_info)
        if all_port:
            self.history(host, port_info, all_port)
            self.update_port_info(all_port, host)
            for port, protocol in all_port.items():
                if port == '19':
                    continue
                banner = ''
                print '----->', port
                add_time = time.strftime('%Y-%m-%d %H:%M:%S')
                protocol = self.mod_protocol(port, protocol)
                asset_id, area_id = self.find_asset_id(host)
                res = self.send_http(host, port)
                content = None
                try:
                    content = self.decode(res)
                except Exception:
                    pass
                if content:
                    print 'http'
                    title = self.re_title(content)
                    header, server = self.mod_headers(res)
                    banner, rule_id = self.find_banner(content, title, header)
                    manufacturer = self.find_manufacturer(content)
                    sql_http = "update tbl_asset_info set protocol=%s,asset_id=%s,title=%s,header=%s,html_page=%s,banner=%s,rule_id=%s,server=%s,manufacturer=%s where IP=%s and port=%s"
                    self.mysql.update(sql_http, (protocol, asset_id, title, header, content, banner, rule_id, server, manufacturer, host, port))
                else:
                    print 'telnet'
                    content = self.telnet(host, port)
                    if content:
                        banner, rule_id = self.find_banner(content)
                        manufacturer = self.find_manufacturer(content)
                        sql_telnet = "update tbl_asset_info set protocol=%s,asset_id=%s,html_page=%s,banner=%s,rule_id=%s,manufacturer=%s where IP=%s and port=%s"
                        self.mysql.update(sql_telnet, (protocol, asset_id, content, banner, rule_id, manufacturer, host, port))
                sql_time = "update tbl_asset_info set update_time=%s where IP=%s and port=%s"
                self.mysql.update(sql_time, (add_time, host, port))
                if content_type == 0:
                    ScanMaster().door(t_id, vul_plug_id, host, int(port), protocol, banner, content)
        else:
            print 'No open ports!'

    def nmap_scan(self, ip):
        cmd = 'nmap -O %s' % (ip)
        stdoutput = None
        try:
            output = os.popen(cmd)
            stdoutput = output.read()
        except Exception:
            pass
        if stdoutput and 'Nmap scan report for' in stdoutput:
            trim = stdoutput.split('\n')
            device_type = ''
            device_info = ''
            all_port = {}
            OS = ''
            for i in trim:
                line = i.lower()
                if 'open' in line and 'warning' not in line and '%' not in line and 'filtered' not in line and 'running' not in line and 'cpe:' not in line and 'nmap scan report' not in line:
                    one = i.split(' ')
                    data = []
                    for j in one:
                        if j:
                            data.append(j)
                    port = data[0].split('/')[0]
                    protocol = data[-1]
                    if port.isdigit():
                        all_port[port] = protocol
                if 'Aggressive OS guesses' in stdoutput:
                    if 'Aggressive OS guesses' in i:
                        OS = self.get_os(i).strip()
                elif 'Running' in i:
                    if ',' in i:
                        i = i.split(',')[0]
                    OS = i.split(':')[-1].strip()
                if 'Device type' in i:
                    device = i.split(':')[-1]
                    if '|' in device:
                        device_list = device.split('|')
                        device_type = ','.join(device_list).strip()
                        device_info = device_list[0].strip()
                    else:
                        device_type = device_info = device.strip()
            return all_port, OS, device_type, device_info
        else:
            return {}, '', '', ''

    def get_os(self, i):
        b = i.split('),')
        for i in b:
            if ',' in i or 'or' in i:
                pass
            else:
                if '(' in i:
                    os = i.split('(')[0].strip()
                    if 'Aggressive OS guesses' in os:
                        os = os.split(':')[-1]
                    return os
if __name__ == '__main__':
    m = AssetDiscovery()
    print m.find_area_id('117.159.37.40')