#coding:utf-8
import re
import log
import time
import datetime
import asset_scan
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
cur = conn.cursor()

def logs():
	info = sys.exc_info()
	level = 4
	lylog = log.LogMaster('scan_log',info,level)
	lylog.buildLog()


def read():
	config_file = open('/var/www/html/ngscanner/static/sconf/scanconfig')
	data = config_file.read( )
	dic = eval(data)
	isopen = dic['isopen']
	cycle = dic['cycle']
	config = int(dic['content'])
	today = time.strftime('%Y-%m-%d',time.localtime(time.time())).split('-')
	Y = int(today[0])
	M = int(today[1])
	D = int(today[2])
	anyday=datetime.datetime(Y,M,D).strftime("%w")

	if isopen:
		sql1 = "select * from tbl_task"
		count = int(cur.execute(sql1))
		if not count:
			try:
				asset_scan.create(config)
			except Exception,e:
				logs()
			return			
		sql = "select end_time,state from tbl_task where scan_type=%s order by id desc"
		cur.execute(sql,(1))
		data = cur.fetchone()
		end_time = str(data[0])
		state = data[1]
		if state != 2:
			return
		if cycle == 'd':
			try:
				asset_scan.create(config)
			except Exception,e:
				logs()
		elif cycle == 'w':
			if anyday == '1':
				try:
					asset_scan.create(config)
				except Exception,e:
					logs()
		elif len(cycle) == 2 and cycle[0] == 'w':
			if anyday == cycle[-1]:
				try:
					asset_scan.create(config)
				except Exception,e:
					logs()
		elif len(cycle) == 2 and cycle[0] == 'm':
			if str(D) == cycle[-1]:
				try:
					asset_scan.create(config)
				except Exception,e:
					logs()
		elif len(cycle) == 2 and cycle[0] == 'd':
			now_time = time.strftime('%Y-%m-%d %H-%M-%S')
			if cycle.strip('d') == '15':
				if mod_time(now_time) == mod_time(end_time,'15d'):
					asset_scan.create(config)
			elif cycle.strip('d') == '30':
				if mod_time(now_time) == mod_time(end_time,'1'):
					asset_scan.create(config)
			elif cycle.strip('d') == '60':
				if mod_time(now_time) == mod_time(end_time,'2'):
					asset_scan.create(config)
			elif cycle.strip('d') == '90':
				if mod_time(now_time) == mod_time(end_time,'3'):
					asset_scan.create(config)
			else:
				pass

def mod_time(ti,d='' ):
	t = ti.split(' ')[0].split('-')
	if d:
		if d[-1] == 'd':
			if int(t[-1])<15:
				t[-1]='15'
			elif int(t[-1])>=15 and int(t[-1])!=30:
				t[-1]='30'
			else:
				t[1]=str(int(t[1])+1)
				if int(t[1])>12:
					t[1] = str(int(t[1])-12)
					t[0]=str(int(t[0])+1)
				if len(t[1]) == 1:
					t[1] = '0'+t[1]
				t[-1]='15'
			return t
		else:
			t = ti.split(' ')[0].split('-')
			t[1]=str(int(t[1])+int(d))
			if int(t[1])>12:
				t[1] = str(int(t[1])-12)
				t[0]=str(int(t[0])+1)
			if len(t[1]) == 1:
				t[1] = '0'+t[1]
			return t
	else:
		return t

if(__name__=="__main__"):
	read()
	# asset_scan.create(config)