#coding:utf-8
import MySQLdb

def connect(host,passwd):
	try:
		conn = MySQLdb.connect(
		        host=host,
		        port = 3306,
		        user='root',
		        passwd=passwd,
		        charset="utf8"
		        )
		if conn: 
			conn.close()
		return 1
	except:
		return 0
def start(host,port,pro):
	try:
		state_list = []
		pass_list = ['123', 'test', '123456', 'password', 'root', 'admin','qaz123','111111']
		for j in pass_list:
			state = connect(host,j)
			if state:
				return 1,'','root:'+j
	except:
		return 0,0,0

