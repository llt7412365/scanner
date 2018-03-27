# coding:utf-8
import os
import time
from start_scan import Asset
from MySqlConn import Mysql
from multiprocessing import Process, Queue, Pool


def func(t_id):
    pid = os.getpid()
    mysql = Mysql()
    sql = "insert into tbl_task_manage (t_id,p_id) values(%s,%s)"
    sql2 = "update tbl_task set state=%s where id=%s"
    mysql.update(sql2, (1, t_id))
    mysql.insertOne(sql, (t_id, pid))
    mysql.dispose()
    Asset().start(t_id)


def write_queue(q):
    while 1:
    	mysql = Mysql()
        if q.full():
            pass
        else:
            size = q.qsize()
            if size < 5:
                surplus_size = 5 - size
                sql = "select id from tbl_task where content_type=2 and scan_type=2 and state=0 and ident=0 order by id asc limit %s;"%surplus_size
                info = mysql.getAll(sql)
                print info
                count = mysql.getCount(sql)

                if count>0:
                    for index, i in enumerate(info, 1):
                        t_id = i['id']
                        q.put(t_id)
                        sql2 = "update tbl_task set state=%s,ident=%s where id=%s"
                        mysql.update(sql2, (4, 1, t_id))

                        if index == surplus_size:
                            break
                mysql.dispose()

        time.sleep(5)


def read_queue(q):
    pool = Pool(processes=3)
    while 1:
        if q.empty():
            time.sleep(5)
        else:
            t_id = q.get()
            pool.apply_async(func, (t_id,))


def pycall():
    q = Queue(10)
    pw = Process(target=write_queue, args=(q,))
    pr = Process(target=read_queue, args=(q,))
    pw.start()
    pr.start()
