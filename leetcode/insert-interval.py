#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

# Definition for an interval.
# class Interval(object):
#     def __init__(self, s=0, e=0):
#         self.start = s
#         self.end = e

class Solution(object):
    def insert(self, intervals, newInterval):
        """
        :type intervals: List[Interval]
        :type newInterval: Interval
        :rtype: List[Interval]
        """
        intervals.append(newInterval)
        intervals.sort(lambda x, y: cmp(x.start, y.start) or cmp(x.end, y.end))
        # print_intervals(intervals)
        res = []
        x, y = intervals[0].start, intervals[0].end
        for i in range(1, len(intervals)):
            a, b = intervals[i].start, intervals[i].end
            assert(x <= a)
            if a <= y:
                y = max(y, b)
            else:
                res.append((x, y))
                x, y = a, b
        res.append((x, y))
        return map(lambda (x, y): Interval(x, y), res)
