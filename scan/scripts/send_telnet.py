# -*- coding: utf-8 -*- 
import sys
import telnetlib
def start():
	host = sys.argv[1]
	user = sys.argv[2]
	password = sys.argv[3]
	tn = telnetlib.Telnet(host, port=23, timeout=10)  
	tn.set_debuglevel(2)
	tn.read_until("\r\nUsername:", timeout=3)
	tn.write(user + "\n")
	tn.read_until("\r\nPassword:", timeout=3)
	tn.write(password + "\n")
	tn.read_all()

try:
	start()
except Exception, e:
	pass
