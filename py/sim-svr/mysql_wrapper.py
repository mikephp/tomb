#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import time
import MySQLdb

# handle broken connection to MySQL if in idle state too long
# and we try to reconnect MySQL server.

class MySQLWrapper():
    def __init__(self, ctor, max_idle = 60):
        self.ctor = ctor
        self.conn = ctor()
        self.ctor_at = time.time()
        self.max_idle = max_idle

    def execute(self, ps, commit = False):
        while True:
            try:
                cur = self.conn.cursor()
                cur.execute(ps)
                if commit: self.conn.commit(); cur.close(); return
                else: return cur # user close it.
            except MySQLdb.OperationalError as e:
                now = time.time()
                if (now - self.ctor_at) > self.max_idle:
                    self.conn = self.ctor()
                    self.ctor_at = now
                    continue
                else:
                    raise
