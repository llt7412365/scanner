# coding:utf-8
import sys
import log
import time
import redis
from MySqlConn import Mysql
from crossroads import ScanMaster


class LeakScan(object):

    def __init__(self):
        self.mysql = Mysql()

    def logs(self):
        info = sys.exc_info()
        level = 4
        lylog = log.LogMaster('scan_log', info, level)
        lylog.buildLog()

    def Redis(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        conn = redis.Redis(connection_pool=pool)
        return conn

    def mod_vul_plug_id(self, vul_plug_id):
        port_list = []
        id_list = []
        if ',' in vul_plug_id:
            id_list = vul_plug_id.split(',')
        else:
            id_list = [vul_plug_id]
        if id_list:
            for i in id_list:
                sql1 = 'select port from sys_vul where id=' + str(i)
                result = self.mysql.getOne(sql1)
                string_port = str(result['port'])
                if ',' in string_port:
                    p_list = string_port.split(',')
                    for port in p_list:
                        port = port.replace(' ', '')
                        if str(port) not in port_list:
                            port_list.append(str(port))
                else:
                    if str(string_port) not in port_list:
                        port_list.append(str(string_port.replace(' ', '')))
            str_port = str(tuple(port_list))
            if len(port_list) == 1:
                str_port = str_port.replace(',', '')
            sql = "select IP,port,protocol,html_page,banner from tbl_asset_info where port IN" + str_port
            return sql
        else:
            return "select IP,port,protocol,html_page,banner from tbl_asset_info"

    def find_range_ip(self, dete_obj):
        ip_list = dete_obj.split('-')
        ip_start = ip_list[0]
        ip_end = ip_list[-1]
        sql = 'select IP,port,protocol,html_page,banner from tbl_asset_info where inet_aton(%s)<= inet_aton(ip) AND inet_aton(%s)>=inet_aton(ip)'
        info = self.mysql.getAll(sql, (ip_start, ip_end))
        count = self.mysql.getCount(sql)
        return count, info

    def find_asset_count(self):
        sql = "select * from tbl_asset where state=%s"
        count = self.mysql.getCount(sql, (1))
        return int(count)

    def process(self, num1, num2):
        a = float(num1)
        b = float(num2)
        sche = "%.f%%" % (b / a * 100)
        return sche

    def scan(self, dete_obj, vul_plug_id, t_id):
        rcon = self.Redis()
        if not rcon.hgetall(t_id):
            rcon.hmset(t_id, {'state': 0, 'count': 0})
        sql1 = "select IP,port,protocol,html_page,banner from tbl_asset_info"
        if vul_plug_id != '0':
            sql1 = self.mod_vul_plug_id(vul_plug_id)
        info = self.mysql.getAll(sql1)
        count = self.mysql.getCount(sql1)
        redis_dic = rcon.hgetall(t_id)
        state = redis_dic['state']
        now_count = int(redis_dic['count'])
        if '-' in dete_obj:
            count, info = self.find_range_ip(dete_obj)
        if count != 0:
            for index, msg in enumerate(info, 1):
                if state == '1':
                    if index <= now_count:
                        continue
                rcon.hincrby(t_id, 'count', amount=1)
                ip = msg['IP']
                port = msg['port']
                protocol = msg['protocol']
                html = msg['html_page']
                banner = msg['banner']
                print ip, port
                try:
                    ScanMaster().door(t_id, vul_plug_id, ip, port, protocol, banner, html)
                except Exception:
                    self.logs()
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
        rcon.delete(t_id)
        sql5 = 'delete from tbl_task_manage where t_id=%s'
        self.mysql.delete(sql5, (t_id))
