#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from common2 import *
import os
import traceback
import urlparse

p = Process(debug = True)
pb = PhoneBook('phone-book.db')

root = '/'

# deploy on server.
if os.environ['USER'] == 'ubuntu': root = '/manual/'

def process(env, start_response):
    global p, pb

    path = env['PATH_INFO']
    qs = env['QUERY_STRING']

    # 跳转回主页
    home_ok = """<html><head><meta http-equiv="content-type" content="text/html;charset=utf-8"><meta http-equiv="refresh" content="2; url=%s"/></head><body><p>更新成功，2秒后跳回主页面</p></html>""" % (root)
    home_f1 = """<html><head><meta http-equiv="content-type" content="text/html;charset=utf-8"><meta http-equiv="refresh" content="2; url=%s"/></head><body><p>更新失败，2秒后跳回主页面</p></body></html>""" % (root)
    home_f2 = """<html><head><meta http-equiv="content-type" content="text/html;charset=utf-8"></head><body><p>出现如下异常</p><pre>%s</pre></body></html>"""

    if path == '/':
        phone = pb.randomly_select_phone()
        if not phone:
            start_response('200 OK', [('Content-Type','text/html')])
            return ('<html><body><p>ALL DONE!!!</p></body></html>',)
        try:
            count = pb.count_unmarked_phone()
            (ok, res) = p.above_half(phone, True)
            uid = res
            start_response('200 OK', [('Content-Type','text/html')])
            vcode = './static/%s.jpg' % (p.captcha_filename(uid))
            kvs = {'vcode': vcode, 'uid': uid, 'phone': phone, 'count': count}
            kvs['root'] = root
            html ="""
<html><body><p>Rest: %(count)d</p><p>Phone: %(phone)s</p><img src="%(vcode)s"/>
<form action="%(root)scont" method="GET">
<p>Code: <input type="text" name="code" autofocus/></p>
<input type="hidden" name="phone" value="%(phone)s"/>
<input type="hidden" name="uid" value="%(uid)s"/>
<input type="submit" value="Next"/>
</form>
</body></html>""" % kvs
            return (html,)
        except Exception as e:
            bt = traceback.format_exc()
            return (home_f2 % bt,)

    elif path == '/cont':
        d = urlparse.parse_qs(qs)
        phone = d['phone'][0]
        code = d['code'][0]
        uid = d['uid'][0]
        try:
            (ok, res) = p.bottom_half(uid, code)
            if ok:
                balance = res
                pb.update_phone_balance(phone, balance)
                print "更新号码 '%s' = %s 成功" % (phone, balance)
                start_response('200 OK',[('Content-Type','text/html')])
                return (home_ok,)
            else:
                print "更新号码 '%s' 失败" % (phone)
                start_response('200 OK',[('Content-Type','text/html')])
                return (home_f1,)
        except Exception as e:
            bt = traceback.format_exc()
            return (home_f2 % bt,)

    else: # others as jpeg files.
        fname = path[1:]
        if os.path.exists(fname):
            start_response('200 OK',
                            [('Content-Type','applicaiton/jpeg')])
            data = open(fname).read()
            return (data,)
        else:
            start_response('400 Not Found', [('Content-Type','text/html')])
            return ('',)

def run(env, start_response):
    return process(env, start_response)

if __name__ == '__main__':
    from wsgiref.validate import validator
    from wsgiref.simple_server import make_server
    vrun=validator(run)
    httpd = make_server('', 8000, vrun)
    httpd.serve_forever()
