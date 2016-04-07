#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import hashlib
import werobot
import sys

token = 'Ut39VRSFwpqOFBFnAszaLKdRmO3o'
robot = werobot.WeRoBot(token=token, enable_session = True)

@robot.handler
def echo(message, session):
    return 'Hello World!'

if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    robot.run(port = port)
