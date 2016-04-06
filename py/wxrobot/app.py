#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from flask import Flask
from flask import make_response, redirect, url_for
from flask import request as AppRequest
from flask import render_template
import hashlib
import werobot
import sys

app = Flask(__name__)
token = 'Ut39VRSFwpqOFBFnAszaLKdRmO3o'
robot = werobot.WeRoBot(token=token, enable_session = True)

@app.route('/', methods = ['GET'])
def validate():
    sign = AppRequest.args.get('signature', '')
    ts = AppRequest.args.get('timestamp', '')
    nonce = AppRequest.args.get('nonce', '')
    echostr = AppRequest.args.get('echostr', '')
    ss = [ts, nonce, token]
    ss.sort()
    sign2 = hashlib.sha1(''.join(ss)).hexdigest()
    if sign == sign2:
        return echostr
    return 'OK'

@robot.handler
def echo(message, session):
    return 'Hello World!'

if __name__ == '__main__':
    cmd = 'robot'
    port = 8080
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    if cmd == 'robot':
        robot.run(port = port)
    elif cmd == 'app':
        app.run('0.0.0.0', port, debug = True)
    else:
        print 'Unknown command %s' % cmd
