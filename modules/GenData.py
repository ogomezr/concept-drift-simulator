#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 13:20:01 2020

@author: Oscar
"""
import numpy as np

def straighLine(x, m, n):
    y = m * x + n
    return y


def polFunc(x, a, b, c, d):
    y = (a * x**3) + (b * x**2) + c * x + d
    return y


def sinFunc(x, m, n, a, w, ph):
    y = m * x + a * (np.sin(w * x + ph)) + n
    return y


def genData(typeData,X,slope,axisY,a,b,c,d,amplitude,angular,phase):
    func = {
        'straighLine': straighLine(X, slope, axisY),
        'polinomial': polFunc(X, a, b, c, d),
        'senoidal': sinFunc(X, slope, axisY, amplitude, angular, phase)
    } 
    return func[typeData] 