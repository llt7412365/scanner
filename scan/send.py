# coding:utf-8
import re
import sys
import chardet
import telnetlib
from timeout import timeout


@timeout(1)
def read_all(tn):
    data = tn.read_all()
    return data


def decode2(data):
    char = chardet.detect(data)
    encoding = char.get('encoding')
    data1 = data.decode(encoding).encode('utf-8')
    str_list = []
    for i in data1:
        if i.isalnum():
            str_list.append(i)
        elif i in re.findall(r'((?=[\x21-\x7e]+)[^A-Za-z0-9])', data):
            str_list.append(i)
        elif i == '\n':
            str_list.append(i)
        else:
            str_list.append(' ')
    content = ''.join(str_list)
    return content


def telnet(ip, port):
    tn = telnetlib.Telnet(ip, port, timeout=10)
    try:
        return read_all(tn)
    except Exception:
        pass
    data = tn.read_i_need()
    return data


def start():
    ip = sys.argv[1]
    port = sys.argv[2]
    content = ''
    try:
        content = decode2(telnet(ip, port))
    except Exception:
        pass
    print content
if __name__ == '__main__':
    start()