#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 19:34:21 2020

@author: Oscar
"""


class PageHinkleyTest:
    def __init__(self, admissibleChange, threshold, minCont):
        self.admissibleChange = admissibleChange
        self.threshold = threshold
        self.n = 0
        self.mT = 0
        self.MT = 1
        self.MTmax = 0
        self.sumError = 0
        self.change = False
        self.PH = []
        self.PHmax = []
        self.acummT = []
        self.meanError = 0
        self.cont = 0
        self.minCont = minCont

    def runTest(self, x):
        self.n += 1
        self.sumError += x
        self.meanError = (x + self.meanError * (self.n - 1)) / self.n
        self.mT = max(0, 0.94 * self.mT +
                      (x - self.meanError - self.admissibleChange))
        self.MT = min(self.MT, self.mT)
        pH = self.mT - self.MT
        self.acummT.append(self.sumError)
        self.cont += 1
        return pH >= self.threshold

