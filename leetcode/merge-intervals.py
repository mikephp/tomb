#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def merge(self, intervals):
        """
        :type intervals: List[Interval]
        :rtype: List[Interval]
        """
        if not intervals: return []
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

# Definition for an interval.
class Interval(object):
    def __init__(self, s=0, e=0):
        self.start = s
        self.end = e

def list_to_intervals(xs):
    return map(lambda x: Interval(x[0], x[1]), xs)

def print_intervals(xs):
    print ', '.join(map(lambda x: '[%d, %d]' % (x.start, x.end), xs))
    
if __name__ == '__main__':
    s = Solution()
    print_intervals(s.merge(list_to_intervals([[1,3],[2,6],[8,10],[15,18]])))
    print_intervals(s.merge(list_to_intervals([[1,4], [0, 4]])))
