#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from common2 import *
from PIL import Image
import traceback

def main():
    p = Process(debug = True)
    pb = PhoneBook('phone-book.db')
    while True:
        phone = pb.randomly_select_phone()
        if not phone: print 'ALL DONE!!!'; break
        print '-----获取验证码-----'
        try:
            (ok, res) = p.above_half(phone)
        except Exception as e:
            print '-----获取验证码失败-----'
            traceback.print_exc()
            continue
        if not ok:
            uid = res
            im = Image.open('./static/%s.jpg' % (p.captcha_filename(uid)))
            im.show()
            code = raw_input('input code > ').strip()
            try:
                print '-----查询余额-----'
                (ok, res) = p.bottom_half(uid, code)
                if not ok:
                    print '-----查询余额失败-----'
                    continue
            except Exception as e:
                print '-----查询余额发生异常-----'
                continue
        balance = res
        pb.update_phone_balance(phone, balance)
        print "更新号码 '%s' = %s 成功" % (phone, balance)

if __name__ == '__main__':
    main()
