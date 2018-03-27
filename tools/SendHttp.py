#coding:utf-8
import ssl
import time
import warnings
import requests
from selenium import webdriver
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")


def send1(url):
    if 'https' in url:
        try:
            res = requests.get(url, timeout=5, verify=False)
            return res
        except Exception:
            return
    else:
        try:
            res = requests.get(url, timeout=5)
            return res
        except Exception:
            return


def mod_url(host, port, protocol):
    url = ''
    if protocol == 'https':
        url = 'https://' + host + ':' + str(port)
    else:
        url = 'http://' + host + ':' + str(port)
    return url


def send2(url):
    service_args = []
    service_args.append('--load-images=no')  # 图片加载
    service_args.append('--ignore-ssl-errors=true')  # 忽略https错误
    service_args.append('--ssl-protocol=any')
    browser = webdriver.PhantomJS(service_args=service_args, executable_path='/opt/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
    browser.set_page_load_timeout(20)
    browser.get(url)
    time.sleep(3)
    html = browser.page_source
    browser.quit()
    return html


def mod_headers(res):
    header = ''
    server = ''
    scheme = ''
    if res:
        url = res.url
        scheme = 'HTTP'
        if url.startswith('https:'):
            scheme = 'HTTPS'
        code = res.status_code
        reason = res.reason
        h = res.headers
        he = dict(h)
        data = []
        data.append(scheme + '/' + str(code) + ' ' + reason + '\n')
        for i in h:
            data.append(i + ':' + h[i] + '\n')
        header = ''.join(data).strip()
        server = None
        if 'Server' in he:
            server = he['Server']
    return header, server, scheme.lower()


def decode(req):
    encoding = req.encoding
    if encoding == 'ISO-8859-1':
        encodings = requests.utils.get_encodings_from_content(req.text)
        if encodings:
            encoding = encodings[0]
        else:
            encoding = req.apparent_encoding
    encode_content = req.content.decode(
        encoding, 'replace').encode('utf-8', 'replace')
    return encode_content


def send(host, port, protocol):
    res = ''
    html = ''
    header = ''
    server = ''
    scheme = ''
    url = mod_url(host, port, protocol)
    if url:
        try:
            res = send1(url)
            html = res.content
        except Exception:
            pass
        if res:
            try:
                html = decode(res)
            except Exception, e:
                pass
            if html:
                if judge(html):
                    try:
                        html = send2(url).encode('utf-8')
                    except Exception,e:
                        print e
                        pass
    try:
        header,server, scheme = mod_headers(res)
    except Exception:
        pass
    return html, header, server, scheme


def judge(msg):
    methods = ['window.location', 'window.location.href', 'window.location', 'window.navigate', 'window.loction.replace', 'self.location', 'top.location', 'document.location.replace']
    for met in methods:
        if met in msg:
            return 1
    if 'screen.availHeight' in msg and 'screen.availWidth' in msg and 'window.open' in msg:
        return 1

if __name__ == '__main__':
	pass