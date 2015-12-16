#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import sys
import math

# compute distance between two gps points.
def haversineDistance(lat1, lon1, lat2, lon2):
    R = 6371 # km

    def toRadians(degree):
        return degree * math.pi / 180
    lat_delta = toRadians(lat2 - lat1)
    lon_delta = toRadians(lon2 - lon1)

    lat1 = toRadians(lat1)
    lat2 = toRadians(lat2)

    a = math.sin(lat_delta/2) * math.sin(lat_delta/2) + math.cos(lat1) * math.cos(lat2) * math.sin(lon_delta/2) * math.sin(lon_delta/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d

if __name__ == '__main__':
    print haversineDistance(22.520525, 113.93145, 22.530525, 113.94145)
