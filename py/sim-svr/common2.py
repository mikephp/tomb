#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import os
import re

import redis
import string
import json
import traceback
import socket
import httplib
import uuid
import sqlite3
import random

class PhoneBook:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def randomly_select_phone(self):
        c = self.conn.cursor()
        c.execute('SELECT phone FROM pb WHERE marked = 0 LIMIT 16')
        ps = c.fetchall()
        c.close()
        if len(ps) == 0: return None
        idx = random.randint(0, len(ps) - 1)
        p = str(ps[idx][0])
        return p

    def update_phone_balance(self, phone, balance):
        c = self.conn.cursor()
        c.execute('UPDATE pb SET balance = ?, marked = 1 WHERE phone = ?', (balance, phone,))
        self.conn.commit()
        c.close()

    def count_unmarked_phone(self):
        c = self.conn.cursor()
        c.execute("SELECT count(*) FROM pb where marked = 0")
        count = c.fetchone()[0]
        c.close()
        return count

class Storage:
    def __init__(self):
        self.rh = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 1)

    def get_phone_balance(self, phone_no):
        bal = self.rh.get('pb_' + phone_no)
        if bal: bal = float(bal)
        return bal
    def set_phone_balance(self, phone_no, bal):
        self.rh.setex('pb_' + phone_no, 3600 * 24, bal)

    def get_query_session(self, sid):
        sinfo = self.rh.get('ss_' + sid)
        return sinfo
    def set_query_session(self, sid, sinfo):
        self.rh.setex('ss_' + sid, 10 * 60, sinfo)
    def del_query_session(self, sid):
        self.rh.delete('ss_' + sid)

class Session:
    def __init__(self, debug = False):
        self.cookies = {}
        self.debug = debug

    def from_json(self, s):
        self.cookies = json.loads(s)
    def to_json(self):
        return json.dumps(self.cookies)

    def update_from_string(self, v):
        if not v: return
        ss = v.split(', ')
        for s in ss:
            s = s.split(';')[0].strip()
            try:
                (sk, sv) = s.split('=')
                if self.debug: print '# set-cookie: %s = %s'%(sk, sv)
                self.cookies[sk] = sv
            except Exception as e:
                if self.debug: traceback.print_exc()
    def to_string(self):
        return string.join(map(lambda k : '%s=%s'%(k, self.cookies[k]), self.cookies), '; ')

class HttpPool:
    def __init__(self, connect_timeout = 10, socket_timeout = 10, debug = False):
        self.http = {}
        self.https = {}
        self.connect_timeout = connect_timeout
        socket.setdefaulttimeout(socket_timeout)
        self.debug = debug

    def default_headers(self):
        headers = {}
        headers['Connection'] = 'keep-alive'
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.56'
        # headers['Accept-Encoding'] = 'gzip,deflate'
        headers['Accept-Language'] = 'en-US,en;q=0.8,zh-CN;q=0.6'
        return headers

    def get_http(self, host):
        if host in self.http:
            if self.debug: print 'reused http connection'
            return self.http[host]
        conn = httplib.HTTPConnection(host, timeout = self.connect_timeout)
        self.http[host] = conn
        return conn

    def get_https(self, host):
        if host in self.https:
            if self.debug: print 'reused https connection'
            return self.https[host]
        conn = httplib.HTTPSConnection(host, timeout = self.connect_timeout)
        self.https[host] = conn
        return conn

class Process:
    def __init__(self, debug = False):
        self.debug = debug
        self.st = Storage()
        self.cp0 = HttpPool(debug = debug)
        self.cp1 = HttpPool(debug = debug)
        self.cp = None

    def captcha_filename(self, uid): return '%s' % uid

    def step1(self, cm, cp, headers, init = False):
        if self.debug: print '-----step1-----'
        host = 'zj.ac.10086.cn'
        headers['Host'] = host
        headers['Cookie'] = cm.to_string()
        conn = cp.get_https(host)
        req = conn.request('GET', '/login', '', headers)
        res = conn.getresponse()
        cm.update_from_string(res.getheader('set-cookie'))
        res.read() # discard it.
        if init: conn.close(); return

        # todo(dirlt): generate uid for this query.
        uid = str(uuid.uuid4())
        uid = uid.replace('-','')

        req = conn.request('GET', '/ImgDisp', '', headers)
        res = conn.getresponse()
        f = open('./static/%s.jpg' % (self.captcha_filename(uid)), 'w')
        f.write(res.read())
        f.close()
        conn.close()
        return uid

    def step2(self, cm, cp, headers, phone, code):
        if self.debug: print '-----step2-----'
        host = 'zj.ac.10086.cn'
        headers['Host'] = host
        headers['Content-Length'] = '263'
        headers['Cache-Control'] = 'max-age=0'
        headers['Origin'] = 'https://zj.ac.10086.cn'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Referer'] =  'https://zj.ac.10086.cn/login'
        headers['Cookie'] = cm.to_string()
        body = 'service=my&continue=%2Fmy%2Flogin%2FloginSuccess.do&failurl=https%3A%2F%2Fzj.ac.10086.cn%2Flogin&style=1&pwdType=2&SMSpwdType=0&billId=' + phone + '&passwd1=%CD%FC%BC%C7%C3%DC%C2%EB%A3%BF%BF%C9%D3%C3%B6%AF%CC%AC%C3%DC%C2%EB%B5%C7%C2%BC&passwd=150792&validCode=' + code

        conn = cp.get_https(host)
        req = conn.request('POST', '/loginbox', body, headers)
        res = conn.getresponse()
        if self.debug: print res.status
        if res.status != 200: conn.close(); return
        cm.update_from_string(res.getheader('set-cookie'))
        page = res.read()
        conn.close()
        m = re.search(r'name="SAMLart" value="([\w\d]+)"', page)
        SAMLart = m.groups()[0]
        if self.debug: print 'SAMLart =', SAMLart
        return SAMLart

    def step3(self, cm, cp, headers, SAMLart):
        if self.debug: print '-----step3-----'
        host = 'www.zj.10086.cn'
        headers['Host'] = host
        headers['Content-Length'] = '97'
        headers['Cookie'] = cm.to_string()
        body = 'SAMLart=' + SAMLart + '&RelayState=%2Fmy%2Flogin%2FloginSuccess.do&submit=Submit'

        conn = cp.get_http(host)
        req = conn.request('POST', '/my/sso', body, headers)
        res = conn.getresponse()
        if res.status != 200 and res.status != 302: conn.close(); return
        cm.update_from_string(res.getheader('set-cookie'))
        page = res.read()
        conn.close()
        m = re.search(r"name='SAMLart' value='([\w\d]+)'", page)
        SAMLart = m.groups()[0]
        if self.debug: print 'SAMLart =', SAMLart
        return SAMLart

    def step4(self, cm, cp, headers, SAMLart):
        if self.debug: print '-----step4-----'
        host = 'www.zj.10086.cn'
        headers['Content-Length'] = '224'
        headers['Origin'] = 'http://www.zj.10086.cn'
        headers['Referer'] = 'http://www.zj.10086.cn/my/sso'
        headers['Cookie'] = cm.to_string()
        body = 'RelayState=%252Fmy%252Flogin%252FloginSuccess.do&SAMLart=' + SAMLart + '&jumpUrl=%252Fmy%252Flogin%252FloginSuccess.do&loginUrl=http%253A%252F%252Fwww.zj.10086.cn%252Fmy%252Flogin%252Flogin.jsp&submit=Submit'

        conn = cp.get_http(host)
        req = conn.request('POST','/my/UnifiedLoginClientServlet', body, headers)
        res = conn.getresponse()
        cm.update_from_string(res.getheader('set-cookie'))
        page = res.read()
        conn.close()

    def step5(self, cm, cp, headers):
        if self.debug: print '-----step5-----'
        host = 'www.zj.10086.cn'
        del headers['Content-Length']
        del headers['Content-Type']
        del headers['Origin']
        del headers['Referer']
        headers['Cookie'] = cm.to_string()

        conn = cp.get_http(host)
        req = conn.request('GET','/my/login/loginSuccess.do', headers = headers)
        res = conn.getresponse()
        cm.update_from_string(res.getheader('set-cookie'))
        page = res.read()
        conn.close()

    def step7(self, cm, cp, headers):
        if self.debug: print '-----step7-----'
        host = 'www.zj.10086.cn'
        headers['Host'] = host
        headers['Cookie'] = cm.to_string()
        conn = cp.get_http(host)
        req = conn.request('GET','/my/include/mybill.jsp', headers = headers)
        res = conn.getresponse()
        cm.update_from_string(res.getheader('set-cookie'))
        page = res.read()
        conn.close()
        m = re.search(r'http://service.zj.10086.cn/yw/bill/billDetail.do\?bid=([\w\d]+)&month=0', page)
        url = '/yw/bill/billDetail.do?bid=%s&month=0'%(m.groups()[0])
        return url

    def step8(self, cm, cp, headers, url):
        if self.debug: print '-----step8-----'
        host = 'service.zj.10086.cn'
        headers['Host'] = host
        headers['Cookie'] = cm.to_string()
        conn = cp.get_http(host)
        req = conn.request('GET', url, headers = headers)
        res = conn.getresponse()
        cm.update_from_string(res.getheader('set-cookie'))
        page = res.read()
        conn.close()
        def to_gb2312(s): return s.decode('utf-8').encode('gb2312')
        def to_utf8(s): return s.decode('gb2312').encode('utf-8')
        rex1 = r'<b>%s</b></th><td width="\d+" align="left" class="money">([\S]+) '%(to_gb2312('充值账户实际可用余额/充值账户余额'))
        m1 = re.search(rex1, page)
        rex2 = r'<tr><th><strong>%s</strong>%s</th><td>([^<]+)</td></tr><tr><th><strong>%s</strong>%s</th><td>(\d+)</td></tr' % (to_gb2312('客　　户'),
                                                                                                                                 to_gb2312('：'),
                                                                                                                                 to_gb2312('号　　码'),
                                                                                                                                 to_gb2312('：'))
        m2 = re.search(rex2, page)
        (balance, company, number) = (m1.groups()[0], to_utf8(m2.groups()[0]), m2.groups()[1])
        return (balance, company, number)

    def get_phone_balance(self, cm, cp, headers, phone, code):
        SAMLart = self.step2(cm, cp, headers, phone, code)
        if not SAMLart: return 'mismatch' # 密码，用户名，验证码不匹配
        SAMLart = self.step3(cm, cp, headers, SAMLart)
        if not SAMLart: return
        self.step4(cm, cp, headers, SAMLart)
        self.step5(cm, cp, headers)
        url = self.step7(cm, cp, headers)
        return self.step8(cm, cp, headers, url)

    def above_half(self, phone, bypass = False):
        self.cp = self.cp0 # 在第一阶段使用cp0 pool.
        bal = self.st.get_phone_balance(phone)
        if bal and not bypass: return (True, bal)
        cm = Session()
        # initiate
        self.step1(cm, self.cp, self.cp.default_headers(), True)
        uid = self.step1(cm, self.cp, self.cp.default_headers(), False)
        info = {'sinfo': cm.to_json(),
                'phone': phone}
        self.st.set_query_session(uid, json.dumps(info))
        return (False, uid)

    def bottom_half(self, uid, code):
        self.cp = self.cp1 # 在第二阶段使用cp1 pool.
        cm = Session()
        info = self.st.get_query_session(uid)
        if not info: return (False, 'invalid')
        # self.st.del_query_session(uid)
        info = json.loads(info)
        cm.from_json(info['sinfo'])
        phone = info['phone']
        res = self.get_phone_balance(cm, self.cp, self.cp.default_headers(), phone, code)
        if not res: return (False, 'exception')
        if res == 'mismatch': return (False, 'mismatch')
        bal = res[0]
        self.st.set_phone_balance(phone, bal)

        # for image pattern recognition.
        try:
            os.rename('./static/%s.jpg' % (self.captcha_filename(uid)), './static/vr-%s.jpg' % (code))
        except Exception as e:
            if self.debug: print e
        return (True, bal)

def test():
    p = Process(debug = True)
    phone = raw_input('input phone > ').strip()
    (ok, res) = p.above_half(phone)
    if ok:
        print 'balance = ', res
        return
    uid = res
    from PIL import Image
    im = Image.open('./static/%s.jpg' % (p.captcha_filename(uid)))
    im.show()
    code = raw_input('input code > ').strip()
    (ok, res) = p.bottom_half(uid, code)
    if not ok: print 'query failed: %s' % res; return
    print 'balance = ' , res

if __name__ == '__main__':
    test()
