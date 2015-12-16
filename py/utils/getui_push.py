#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import sys
sys.path.append('../lib/')
sys.path.append('../lib/igetui')
from igt_push import *
from igetui.template import *
from igetui.template.igt_base_template import *
from igetui.template.igt_transmission_template import *
from igetui.template.igt_link_template import *
from igetui.template.igt_notification_template import *
from igetui.template.igt_notypopload_template import *
from igetui.template.igt_apn_template import *
from igetui.igt_message import *
from igetui.igt_target import *
from igetui.template import *

kURL = "http://sdk.open.api.igexin.com/apiex.htm"
keys = {"com.dirlt": # channel key
        ("appkey", "mastersecret", "appid") }

class Token:
    def __init__(self, t, apnm, getui_client_id, ios_device_token):
        self.t = t
        self.apnm = apnm
        self.getui_client_id = getui_client_id
        self.ios_device_token = ios_device_token
class Handler:
    def __init__(self, appKey, masterSecret, appId):
        self.appKey = appKey
        self.masterSecret = masterSecret
        self.appId = appId
        self.push = IGeTui(kURL, appKey, masterSecret)

def _getHandler(apnm):
    (appKey, masterSecret, appId) = keys[apnm]
    return Handler(appKey, masterSecret, appId)

def getHandlerByToken(token): return _getHandler(token.apnm)

# 对于透传来说ios多了一个选择，可以使用ios_device_token来发送.
# 虽然文档说“由于在iOS中只有当应用启动时才能通过个推SDK进行推送（未启动应用时通过APNS进行推送）”
# 但是有时候也可以使用push_template + transmission_template来完成. 不过为了保险还是用这个.
def ios_push_tranmission(token, message = '', payload = ''):
    if not token.ios_device_token: return
    handler = getHandlerByToken(token)
    template = APNTemplate()
    # for APNS.
    template.setPushInfo("", 1, message, "", payload, "", "", "")
    msg = IGtSingleMessage()
    msg.data = template
    ret = handler.push.pushAPNMessageToSingle(handler.appId, token.ios_device_token, msg)
    return ret

def push_template(token, template):
    if not token.getui_client_id: return
    handler = getHandlerByToken(token)

    msg = IGtSingleMessage()
    msg.data = template
    msg.isOffline = True
    msg.offlineExpireTime = 1000 * 3600 * 24
    msg.pushNetWorkType = 0

    target = Target()
    target.appId = handler.appId
    target.clientId = token.getui_client_id
    ret = handler.push.pushMessageToSingle(msg, target)
    return ret

# 通知栏显示，但是进入之后没有对话框. 这种提醒设计应该不希望用户中断当前操作。
def transmission_template(token, message = '', payload = ''):
    handler = getHandlerByToken(token)
    template = TransmissionTemplate()
    template.transmissionType = 1
    template.appId = handler.appId
    template.appKey = handler.appKey
    template.transmissionContent = payload
    # for APNS.
    template.setPushInfo("", 1, message, "", payload, "", "", "")
    return template

# 通知栏显示，点击进入可以看到对话框
def notification_template(token, title = '', message = '', payload = ''):
    handler = getHandlerByToken(token)
    template = NotificationTemplate()
    template.appId = handler.appId
    template.appKey = handler.appKey
    template.title = title
    template.text = message
    template.logo = ""
    template.logoURL = ""
    template.isRing = True
    template.isVibrate = True
    template.isClearable = True
    template.transmissionType = 1
    template.transmissionContent = payload
    # for APNS.
    template.setPushInfo("", 1, message, "", payload, "", "", "")
    return template

# 通知栏显示，点击进入可以看到对话框并且可以打开链接
def weblink_template(token, title = '', text = '', url = '', payload = ''):
    handler = getHandlerByToken(token)
    template = LinkTemplate()
    template.appId = handler.appId
    template.appKey = handler.appKey
    template.title = title
    template.text = text
    template.logo = ""
    template.url = url
    template.transmissionType = 1
    template.transmissionContent = payload
    template.isRing = True
    template.isVibrate = True
    template.isClearable = True
    # for APNS.
    template.setPushInfo("", 1, text, "", payload, "", "", "")
    return template
