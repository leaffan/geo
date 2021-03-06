#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import random
from bisect import bisect_right


class WeightedRandomGenerator():
    def __init__(self, weights):
        self.totals = list()
        running_total = 0
        for w in weights:
            running_total += w
            self.totals.append(running_total)

    def next(self):
        rnd = random() * self.totals[-1]
        return bisect_right(self.totals, rnd)

    def __call__(self):
        return self.next()


def floatrange(start, stop, step):
    while start < stop:
        yield start
        start += step
