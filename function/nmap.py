
'''
使用python-nmap模块对指定ip或ip段进行端口发现，
并对返回数据进行解析并存储进mongodb
'''

def start_nmap(msg):
    #开始nmap扫描
    mysql = Mysql()
    db = mongodb()
    up_ip = []
    in_ip = []
    i_id, sip, eip, rip, ports, t_id = msg
    old_ip = mod_old_list(sip, eip)
    company, group_id, user_id = find_group(i_id)
    if t_id:
        sql = 'select ports from tbl_task where id=%s'
        result = mysql.getOne(sql, (t_id))
        if result:
            ports = result['ports']
    str_ports = get_port(ports)
    nm = nmap.PortScanner()
    arg = '-T4 -O'
    if str_ports != '0':
        arg = '-T4 -O -p' + str_ports
    result = nm.scan(rip, arguments=arg)
    data_list = []
    if result:
        scan_msg = result['scan']
        if scan_msg:
            if scan_msg:
                for ip in scan_msg:

                    device_type = ''
                    device_info = ''
                    system = ''
                    port_info = {}
                    port_list = []
                    try:
                        osclass = scan_msg[ip]['osclass']
                    except:
                        osclass = ''
                    if osclass:
                        device_type = osclass[0]['type']
                        device_info = osclass[0]['info']
                    osmatch = scan_msg[ip]['osmatch']
                    if osmatch:
                        system = osmatch[0]['name']
                        if ',' in system:
                            system = system.split(',')[0]
                    ip_dic = scan_msg[ip]
                    if 'tcp' in ip_dic:
                        port_dic = ip_dic['tcp']
                        for port in port_dic:
                            port_msg = port_dic[port]

                            state = port_msg['state']
                            if state == 'open':
                                port_msg = eval(str(port_msg).replace("u'", "r'"))
                                protocol = port_msg['name'].decode("string_escape")
                                port_info[str(port)] = protocol
                                port_list.append(str(port) + ':' + protocol)
                    if port_info:

                        data_dic = {
                            'ip': ip,
                            'device_type': device_type,
                            'device_info': device_info,
                            'os': system,
                            'port_info': port_info
                        }
                        data_list.append(data_dic)

    if data_list:
        dic = {
            'i_id': str(i_id),
            'sip': sip,
            'eip': eip,
            'ip_range': rip,
            'data': data_list,
            'state': 0,
            'ident': 0
        }
        try:
            db.tbl_info.insert_one(dic)
        except Exception, e:
            logs()
            print '----------------220-------------------'
        sql2 = "update tbl_manage_ip set state=%s where id=%s"
        mysql.update(sql2, (1, i_id))
        mysql.dispose()
    else:
        time.sleep(10)
        sql2 = "update tbl_manage_ip set state=%s where id=%s"
        mysql.update(sql2, (2, i_id))
        DataMaster().creat_task(i_id, sip, eip)
        mysql.dispose()
