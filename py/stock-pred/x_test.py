#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import numpy as np


def rev_bb(prices, ratio=2):
    A = prices.shape[0] + 1
    B = ratio
    mean = np.mean(prices, axis=0)
    std = np.std(prices, axis=0)
    C = (A - 1) * mean
    D = (A - 1) * (std ** 2 + mean ** 2)
    B2 = B ** 2
    a = (B2 - (A - 1)) * (A - 1)
    b = 2 * C * (A - B2 - 1)
    c = A * B2 * D - (B2 + 1) * (C ** 2)

    common = np.sqrt(b ** 2 - 4 * a * c)
    r0 = (common - b) * 0.5 / a
    r1 = (-common - b) * 0.5 / a
    if r0 < r1:
        return (r0, r1)
    else:
        return (r1, r0)
