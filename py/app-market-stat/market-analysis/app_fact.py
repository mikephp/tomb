#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

class AppFact:
    def __init__(self):
        pass
    def to_mongo_doc(self):
        return self.__dict__
    def from_mongo_doc(self, doc):
        self.__dict__ = doc
    def compose_key(self):
        self.key = '%s-%s-%s-%s' % (self.type, self.market,
            self.bundleId, self.version)
