# coding:utf-8
import time
from MySqlConn import Mysql
from bug_scan import LeakScan
from asset_scan import AssetDiscovery


class Asset(object):

    def __init__(self):
        self.mysql = Mysql()

    def createTask(self, config):
        state = 1
        ident = 0
        scan_type = 1
        dete_obj = 'ALL'
        vul_plug_id = '0'
        content_type = config
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        task_name = "AUTO" + time.strftime('%Y%m%d%H%M')
        sql1 = "insert into tbl_task (start_time,task_name,dete_obj,vul_plug_id,scan_type,content_type,add_time,state,ident) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        _id = self.mysql.insertOne(sql1, (now_time, task_name, dete_obj, vul_plug_id, scan_type, content_type, now_time, state, ident))
        t_id = int(_id)
        if content_type == 2:
            LeakScan().scan(dete_obj, vul_plug_id, t_id)
        else:
            AssetDiscovery().find_asset(dete_obj, content_type, vul_plug_id, t_id)
        end_time = time.strftime('%Y-%m-%d %H:%M:%S')
        asset_count = self.find_asset_count()
        sql2 = "update tbl_task set end_time=%s,asset_count=%s where id=%s"
        self.mysql.update(sql2, (end_time, asset_count, t_id))

    def find_asset_count(self):
        sql = "select * from tbl_asset where state=%s"
        count = self.mysql.getCount(sql, (1))
        return int(count)



m = Asset()
m.createTask(0)