#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from gevent.queue import Queue, Empty as QueueEmpty
from gevent.event import AsyncResult
from gevent.pool import Pool as ThreadPool
import time
import traceback

class Producer(object):
    def __init__(self, queue_size = 2048):
        self.Q = Queue(maxsize = queue_size)

    def make(self):
        pass

    def run(self):
        items = self.make()
        if not items: return
        for item in items:
            self.Q.put(item)

    def sync(self, qsize = 0, interval = 5):
        while self.Q.qsize() > qsize:
            time.sleep(interval)

class Consumer(object):
    def __init__(self, Q, queue_timeout = 30):
        self.Q = Q
        self.queue_timeout = queue_timeout

    def process(self, item):
        pass

    def run(self):
        while True:
            try:
                item = self.Q.get(timeout = self.queue_timeout)
            except QueueEmpty:
                print('consumer timeout. quit')
                break
            try:
                self.process(item)
            except:
                traceback.print_exc()
            if getattr(self, '_exit', False):
                break

class AsyncQueue(object):
    def __init__(self, worker_fn, worker_number = 2,
                 queue_size = 2048,
                 queue_timeout = 30):
        self.Q = Queue(maxsize = queue_size)
        self.pool = ThreadPool(worker_number)
        def fn():
            while True:
                try:
                    item = self.Q.get(timeout = queue_timeout)
                except QueueEmpty:
                    print('async queue timeout. quit')
                    break
                ar = item['ar']
                data = item['data']
                try:
                    worker_fn(ar, data)
                except:
                    ar.set(None)
                    ar._traceback_info = traceback.format_exc()
        for i in range(worker_number):
            self.pool.spawn(fn)

    def put(self, data):
        ar = AsyncResult()
        item = {'ar': ar, 'data': data}
        self.Q.put(item)
        return ar
