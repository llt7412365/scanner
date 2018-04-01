#!/usr/bin/env python

import socket
import struct
import binascii

import time
timeout=5
socket.setdefaulttimeout(timeout)

connectionRequestStr="\x03\x00\x00\x0b\x06\xe0\x00\x00\x00\x00\x00"
connectInitialStr="\x03\x00\x00\x65\x02\xf0\x80\x7f\x65\x5b\x04\x01\x01\x04\x01\x01\x01\x01\xff\x30\x19\x02\x01\x22\x02\x01\x20\x02\x01\x00\x02\x01\x01\x02\x01\x00\x02\x01\x01\x02\x02\xff\xff\x02\x01\x02\x30\x18\x02\x01\x01\x02\x01\x01\x02\x01\x01\x02\x01\x01\x02\x01\x00\x02\x01\x01\x02\x01\xff\x02\x01\x02\x30\x19\x02\x01\xff\x02\x01\xff\x02\x01\xff\x02\x01\x01\x02\x01\x00\x02\x01\x01\x02\x02\xff\xff\x02\x01\x02\x04\x00"

userRequestStr="\x03\x00\x00\x08\x02\xf0\x80\x28"

def ms12020(host,port=3389):
	vul_code=0
	vul_detail=''
	return_message = [vul_code, vul_detail]
	

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host,port))
		s.send(connectionRequestStr)
		recv=s.recv(100)
		recv_hex=binascii.b2a_hex(recv)
		if cmp(recv_hex,'0300000b06d00000123400')<>0:
			# #print "%s is not RDP" % host
			s.close()
			return return_message
		s.send(connectInitialStr)
		s.send(userRequestStr)
		recv1=s.recv(100)
		user1=binascii.b2a_hex(recv1)[18:22]
#		#print type(int(user1))
		s.send(userRequestStr)
		recv2=s.recv(100)
		user2=binascii.b2a_hex(recv2)[18:22]
#		#print user2
		user3=int(user2)+1001
#		#print user3
		data5='\x03\x00\x00\x0c\x02\xf0\x80\x38'
#		#print user3[2:]
#		#print '\\x0'+user3[2:][0]+'\\x'+user3[2:][1:]
		data4=struct.pack('>H',int(user1))+struct.pack('>H',user3)
		s.send(data5+data4)
		recv3=s.recv(100)
		vul_detail=binascii.b2a_hex(recv3)[14:18]
		#print vul_detail
		if cmp(vul_detail,'3e00')==0:
			return 1
			#print '%s is vulnerable!' % host
			vul_code=1
		else:
			return 0
			#print '%s is not vulnerable' % host
		data6=struct.pack(">H",int(user2))+struct.pack('>H',user3)
		s.send(data5+data6)
		s.recv(100)
		s.close()
	except Exception as e:
		pass
		#print e
def start(host,port,pro):
	try:
		return ms12020(host),'',''
	except:
		return 0,0,0
# print start('221.180.252.47')
