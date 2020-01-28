#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 19:30:25 2020

@author: Oscar
"""

from . import ChooseModel 
from . import PageHinkleyTest
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import PolynomialFeatures

class DetectChangeAlg:
    def __init__(self, sizeBig, sizeSmall, x, y, phAdmissibleChange,
                 phThreshold, mode=['lin', 'knn', 'pol', 'tree']):
        self.xAllData = x
        self.yAllData = y
        self.xData = x
        self.yData = y
        self.sizeBig = sizeBig
        self.sizeSmall = sizeSmall
        self.lenData = len(x)
        self.chooseModel = ChooseModel.ChooseModel()
        self.model = self.chooseModel.chooseBest(x, y, mode)
        self.error = []
        self.ph = PageHinkleyTest.PageHinkleyTest(phAdmissibleChange, phThreshold)
        self.predictedData = 0
        self.changeTime = 0
        self.img = 0
        self.images = []
        self.mode = mode
        self.ini = len(x) - sizeBig
        self.fin = len(x)
        self.modelNames = [self.chooseModel.getBestName()]
        self.conModel = 0
        self.y = self.returnModel(self.model).tolist()
        self.predList = [self.y]
        self.sol = []
        self.debt = False

    def addData(self, x, y):
        self.xAllData = self.xAllData + x
        self.yAllData = self.yAllData + y
        xData = x
        yData = y
        while xData:
            if len(self.xData) == self.sizeBig:
                self.ini += 1
            self.fin += 1
            nextX = xData.pop(0)
            nextY = yData.pop(0)
            self.xData.append(nextX)
            self.yData.append(nextY)
            self.lenData += 1
            if self.lenData > self.sizeBig:
                self.xData.pop(0)
                self.yData.pop(0)
                self.lenData -= 1
            error = self.predict(nextX, nextY)
            if self.ph.runTest(error):
                if self.ph.cont >= self.ph.minCont:
                    self.changeModel()
                    self.ph.cont = 0
                    self.debt = True
            elif self.ph.cont > 0 and self.debt:
                self.changeModel()
                self.ph.cont = 0
                self.debt = False

            if self.changeTime and self.lenData == self.sizeBig:
                self.model = self.chooseModel.chooseBest(
                    self.xData, self.yData, self.mode)
                self.y = self.returnModel(self.model).tolist()
                self.predList.append(self.y)
                self.conModel += 1
                self.ini = (self.fin - self.sizeBig)
                self.changeTime = False
                self.modelNames.append(self.chooseModel.getBestName())

            self.sol.append((self.ini, self.fin, self.conModel))

    def changeModel(self):
        self.xData = self.xData[-self.sizeSmall:]
        self.yData = self.yData[-self.sizeSmall:]
        self.model = self.chooseModel.chooseBest(
            self.xData, self.yData, self.mode)
        self.y = self.returnModel(self.model).tolist()
        self.predList.append(self.y)
        self.conModel += 1
        self.lenData = self.sizeSmall
        self.changeTime = True
        self.ini = (self.fin - self.sizeSmall)
        self.modelNames.append(self.chooseModel.getBestName())

    def getModel(self):
        return self.chooseModel

    def returnModel(self, model):
        r = np.arange(0, 10, 0.1)
        xData = sm.add_constant(r)
        tittle = self.chooseModel.bestModel[1]
        if tittle == "PolynomialRegression":
            polynomial_features = PolynomialFeatures(degree=3)
            xData = polynomial_features.fit_transform(xData)
        yData = model.predict(xData)
        return yData

    def predict(self, x, y):
        yData = y
        xData = [[1., x]]
        tittle = self.chooseModel.bestModel[1]
        if tittle == "PolynomialRegression":
            polynomial_features = PolynomialFeatures(degree=3)
            xData = polynomial_features.fit_transform(xData)
        yPred = self.model.predict(xData)
        # print("predict")
        # print(yPred)
        error = abs(yData - yPred[0])
        self.error.append(error)
        lenData = len(xData)
        self.predictedData += lenData
        return error
