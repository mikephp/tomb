#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

AppID = "wx51c80a0c3424ecf6"
# AppSecret = "13e7c4f443f24a4a0fc6de09043927b2"
AppKey = "8a3fe1ee64b0fb338eaf8aa2fce878d7"
MerchantId = "1242242402"

import xml.dom.minidom as minidom
import uuid
import hashlib
import urllib
import urllib2
import traceback

def append_sign(kvs):
    kvs.sort(lambda x, y: cmp(x[0], y[0]))
    sa = '&'.join(map(lambda x: '{}={}'.format(x[0], x[1]), kvs))
    sb = 'key=' + AppKey
    s = sa + '&' + sb
    m = hashlib.md5()
    m.update(s)
    sign = m.hexdigest().upper()
    kvs.append(('sign', sign))

def to_xml(kvs):
    s = "<xml>" + "\n"
    for (k, v) in kvs:
        s += "<%s>%s</%s>\n" % (k, v, k)
    s += "</xml>"
    return s

def gen_uuid_32():
    return uuid.uuid4().hex

class WXPayer:
    def __init__(self):
        pass

    def gen_order_xml(self, card_num, phone_no):
        kvs = []
        kvs.append(('appid', AppID))
        body = '净化器流量费充值' + phone_no
        kvs.append(('body', body))
        kvs.append(('mch_id', MerchantId))
        nonce_str = gen_uuid_32()
        kvs.append(('nonce_str', nonce_str))
        notify_url = 'http://api.sumcreate.com/sim-svr/wxpay-cb'
        kvs.append(('notify_url', notify_url))
        trade_no = gen_uuid_32()
        kvs.append(('out_trade_no', trade_no))
        kvs.append(('spbill_create_ip', '192.168.1.1'))
        kvs.append(('total_fee', str(int(card_num * 100))))
        kvs.append(('trade_type', 'APP'))
        append_sign(kvs)
        xml = to_xml(kvs)
        # 返回xml数据和商家订单号
        return (xml, trade_no)

    def parse_xml(self, s):
        doc = minidom.parseString(s)
        root = doc.getElementsByTagName('xml')[0]
        kv = {}
        for c in root.childNodes:
            if c.nodeType == c.ELEMENT_NODE:
                k = c.tagName
                v = c.childNodes[0].data.encode('utf-8')
                kv[k] = v
        if kv['return_code'] != 'SUCCESS':
            print 'Failed: return_msg = {}'.format(kv['return_msg'])
            return 'FAIL'
        if kv['result_code'] != 'SUCCESS':
            print 'Failed: err_code = {}, err_code_des = {}'.format(
                kv['err_code'], kv['err_code_des'])
            return 'FAIL'
        return kv

    def submit_order(self, xml):
        # 微信接口申请订单号
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        retry = 3
        while retry:
            try:
                f = urllib2.urlopen(url, data = xml)
                data = f.read()
                kv = self.parse_xml(data)
                if kv == 'FAIL': return 'FAIL'
                prepay_id = kv['prepay_id']
                return prepay_id
            except Exception as e:
                retry -= 1
                traceback.print_exc()
                continue
        return 'FAIL'

    def handle_order(self, data):
        # 处理微信接口回调.
        # 说明微信充值成功
        kv = self.parse_xml(data)
        if kv == 'FAIL': return 'FAIL'
        trade_no = kv['out_trade_no']
        return trade_no

    def query_order(self, trade_no):
        # 查看微信是否充值成功
        kvs = []
        kvs.append(('appid', AppID))
        kvs.append(('mch_id', MerchantId))
        kvs.append(('nonce_str', gen_uuid_32()))
        kvs.append(('out_trade_no', trade_no))
        append_sign(kvs)
        xml = to_xml(kvs)
        url = 'https://api.mch.weixin.qq.com/pay/orderquery'
        retry = 3
        while retry:
            try:
                f = urllib2.urlopen(url, xml)
                data = f.read()
                kv = self.parse_xml(data)
                if kv == 'FAIL': return 'FAIL'
                # http://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=9_2&index=4
                # 'SUCCESS' means OK.
                return kv['trade_state']
            except Exception as e:
                retry -= 1
                traceback.print_exc()
                continue
        return 'FAIL'

def main():
    wx = WXPayer()
    (xml, trade_no) = wx.gen_order_xml(0.01, '15210717839')
    print xml
    s = wx.submit_order(xml)
    print s
    print '===================='
    print wx.query_order('1433137759')

if __name__ == '__main__':
    main()
