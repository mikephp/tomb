#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

# Definition for a point.
class Point(object):
    def __init__(self, a=0, b=0):
        self.x = a
        self.y = b

class Solution(object):
    def maxPoints(self, points):
        """
        :type points: List[Point]
        :rtype: int
        """

        def ok(a, b, c, debug = False):
            u = (b.x - a.x) * (c.y - b.y)
            v = (c.x - b.x) * (b.y - a.y)
            if debug:
                print u, v
            return u == v

        if not points: return 0
        if isinstance(points[0], list):
            points = map(lambda x: Point(x[0], x[1]), points)

        class Pt(object):
            def __init__(self, p, idx, count):
                self.x = p.x
                self.y = p.y
                self.idx = idx
                self.count = count

        # dedup and count.
        points.sort(lambda x, y: cmp(x.x, y.x) or cmp(x.y, y.y))
        ps = []
        pp = points[0]
        c = 0
        for p in points:
            if pp.x == p.x and pp.y == p.y:
                c += 1
            else:
                ps.append(Pt(pp, len(ps), c))
                pp = p
                c = 1
        ps.append(Pt(pp, len(ps), c))

        n = len(ps)
        if n == 1: return ps[0].count

        if False:
            seen = set()
            res = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if (i, j) in seen: continue
                    v = 0
                    for k in range(n):
                        if (v + (n - k)) < res: break
                        if ok(ps[i], ps[j], ps[k]):
                            v += ps[k].count
                            seen.add((j, k))
                    res = max(res, v)
            print 'true = ', res

        def slope(a, b):
            if a.x == b.x: return 1 << 31
            return (b.y - a.y) * 1000.0 / (b.x - a.x)

        from collections import defaultdict
        d = defaultdict(list)
        for i in range(n):
            for j in range(i + 1, n):
                s = slope(ps[i], ps[j])
                d[s].append((i, j))

        # print d
        # NOTE(yan): 按照斜率group, 然后对group里面的pairs进行排序
        # 然后遍历这个pairs, 确保后面的pairs里面有一个点在之前出现过
        # 否则就属于另外一个line.
        res = 0
        for s in d:
            xs = d[s]
            # if len(xs) >= 21:
            #     print xs
            #     print 'OK'
            seen = set()
            xs.sort(lambda x, y: cmp(x[0], y[0]) or cmp(x[1], y[1]))
            for (i, j) in xs:
                if i not in seen and j not in seen:
                    v = sum(map(lambda x: ps[x].count, seen))
                    res = max(res, v)
                    seen.clear()
                seen.add(i)
                seen.add(j)
            v = sum(map(lambda x: ps[x].count, seen))
            res = max(res, v)
        return res

if __name__ == '__main__':
    s = Solution()
    print s.maxPoints([[84,250],[0,0],[1,0],[0,-70],[0,-70],[1,-1],[21,10],[42,90],[-42,-230]])
    print s.maxPoints([[1,1],[1,1],[1,1]])
    print s.maxPoints([[29,87],[145,227],[400,84],[800,179],[60,950],[560,122],[-6,5],[-87,-53],[-64,-118],[-204,-388],[720,160],[-232,-228],[-72,-135],[-102,-163],[-68,-88],[-116,-95],[-34,-13],[170,437],[40,103],[0,-38],[-10,-7],[-36,-114],[238,587],[-340,-140],[-7,2],[36,586],[60,950],[-42,-597],[-4,-6],[0,18],[36,586],[18,0],[-720,-182],[240,46],[5,-6],[261,367],[-203,-193],[240,46],[400,84],[72,114],[0,62],[-42,-597],[-170,-76],[-174,-158],[68,212],[-480,-125],[5,-6],[0,-38],[174,262],[34,137],[-232,-187],[-232,-228],[232,332],[-64,-118],[-240,-68],[272,662],[-40,-67],[203,158],[-203,-164],[272,662],[56,137],[4,-1],[-18,-233],[240,46],[-3,2],[640,141],[-480,-125],[-29,17],[-64,-118],[800,179],[-56,-101],[36,586],[-64,-118],[-87,-53],[-29,17],[320,65],[7,5],[40,103],[136,362],[-320,-87],[-5,5],[-340,-688],[-232,-228],[9,1],[-27,-95],[7,-5],[58,122],[48,120],[8,35],[-272,-538],[34,137],[-800,-201],[-68,-88],[29,87],[160,27],[72,171],[261,367],[-56,-101],[-9,-2],[0,52],[-6,-7],[170,437],[-261,-210],[-48,-84],[-63,-171],[-24,-33],[-68,-88],[-204,-388],[40,103],[34,137],[-204,-388],[-400,-106]])
