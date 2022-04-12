from turtle import position
import grpc

import minecraft_pb2_grpc
from minecraft_pb2 import *

import random
import numpy as np
import math

class KNN:
	def __init__(self, k):
		#KNN state here
		#Feel free to add methods
		self.k = k
		self.data = None
		self.result = None

	def distance(self, featureA, featureB):
		diffs = (featureA - featureB)**2
		return np.sqrt(diffs.sum())

	def train(self, X, y):
		#training logic here
		#input is an array of features and labels
		#Lazy model, thus just store data is sufficient
		self.data = X
		self.result = y

	def predict(self, X):
		#Run model here
		#Return array of predictions where there is one prediction for each set of features
		output = np.zeros(X.shape[0])
		closeNeighbor = np.zeros(self.k)
		row, col = self.data.shape
		distances = np.zeros((self.data.shape[0], 2))
		for i in range(0, X.shape[0]):
			yesCount = 0
			noCount = 0
			for j in range(0, row):
				# excluding the last attribute since that's the prediction
				distances[j, 0] = j
				distances[j, 1] = self.distance(X[i, :], self.data[j, :])

			distances = distances[distances[:, 1].argsort()]

			for z in range(0, self.k):
				if self.result[int(distances[z, 0])] == 1:
					yesCount += 1
				else:
					noCount += 1
			if yesCount >= noCount:
				output[i] = 1
			else:
				output[i] = 0

		return output