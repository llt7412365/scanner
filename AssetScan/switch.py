#coding:utf-8
import os
import sys
import redis
import MySQLdb

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
conn.ping(True)
cur = conn.cursor()

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

def on(t_id):
	sql1 = 'select record from tbl_task_manage where t_id=%s'
	sql2 = 'update tbl_task set ident=%s where id=%s'
	sql3 = 'delete from tbl_task_manage where t_id=%s'
	cur.execute(sql1,(t_id))
	data = cur.fetchone()
	if not data:
		return 2
	record = eval(data[0])
	if not record:
		return 2
	record['state']=1
	record['count']=str(int(record['count'])-1)
	r.hmset(t_id,record)
	cur.execute(sql3,(t_id))
	cur.execute(sql2,(0,t_id))
	return 1


def off(t_id):
	redis_dic = r.hgetall(t_id)
	if not redis_dic:
		return 2
	pid = get_pid(t_id)
	cmd = "kill -9 "+str(pid)
	os.system(cmd)
	sql2 = 'update tbl_task set state=%s where id=%s'
	cur.execute(sql2,(3,t_id))
	sql = "update tbl_task_manage set record=%s where t_id=%s"
	cur.execute(sql,(str(redis_dic),t_id))
	r.delete(t_id)
	return 1

def delete(t_id):
	r.delete(t_id)
	sql = 'select state from tbl_task where id=%s'
	cur.execute(sql,(t_id))
	data = cur.fetchone()
	state = data[0]
	if state == 3:
		sql2 = 'delete from tbl_task where id=%s'
		cur.execute(sql2,(t_id))
		return 1
	return 0


def get_pid(t_id):
	sql = 'select p_id from tbl_task_manage where t_id=%s'
	cur.execute(sql,(t_id))
	data = cur.fetchone()
	pid = data[0]
	return pid

def start():
	t_id = sys.argv[1]
	name = sys.argv[2]
	if name == 'stop':
		try:
			print int(off(t_id))
		except Exception,e:		
			print 0

	else:
		try:
			print int(on(t_id))
		except Exception,e:
			print 0
start()