#coding:utf-8
import os
import sys
import time
import MySQLdb
from multiprocessing import Process, Queue,Pool
data_file = open('/var/www/html/ngscanner/scan/mysql_connect_config')
data = eval(data_file.read())
conn= MySQLdb.connect(
        host=data['host'],
        port = data['port'],
        user=data['user'],
        passwd=data['passwd'],
        db =data['db'],
        charset=data['charset']
        )
cur = conn.cursor()




def func(t_id):
	import asset_scan
	pid = os.getpid()
	sql = "insert into tbl_task_manage (t_id,p_id) values(%s,%s)"
	cur.execute(sql,(t_id,pid))
	asset_scan.start(t_id)

def write_queue(q):
	while 1:
		if q.full():
			pass
		else:
			size = q.qsize()
			if size < 5:
				surplus_size = 5-size
				sql = "select id from tbl_task where scan_type=2 and content_type=2 and state=0 and ident=0"
				data_all=cur.execute(sql)
				info = cur.fetchmany(data_all)
				for index,i in enumerate(info,1):
					t_id = i[0]
					q.put(t_id)
					sql2 = "update tbl_task set ident=%s where id=%s"
					cur.execute(sql2,(1,t_id))
					if index == surplus_size:
						break
		time.sleep(5)

	
def read_queue(q):
	pool = Pool(processes = 2)
	while 1:
		if q.empty():
			time.sleep(5)
		else:
			t_id = q.get()
			pool.apply_async(func, (t_id,))





if __name__ == '__main__':
    q = Queue(10)
    pw = Process(target=write_queue,args=(q,))
    pr = Process(target=read_queue,args=(q,))
    pw.start()
    pr.start()
