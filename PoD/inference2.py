from random import randint
import grpc
import numpy as np
import pandas as pd
from PoD import singleBlockChange
import tensorflow as tf

import minecraft_pb2_grpc
from minecraft_pb2 import *
from PoD import locateMinMax
from worldControl import worldReset

from copy import deepcopy

# Set variables
HOUSE_WIDTH = 13
HOUSE_HEIGHT = 13
HOUSE_DEPTH = 13
ACTION_SPACE = 7

# connect to the server
channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

# block types that we will allow
acceptedBlocks = [5, 41, 60, 88, 131, 160, 224]

# dictionary for one-hot mapping
dict_one_hot_mapping = {5: 0, 41: 1, 60: 2, 88: 3, 131: 4, 160: 5, 224: 6}

# function to generate a random noise block of size n
def generateRandomNoiseBlock(location, size):
    for xAxis in range(location.x, location.x + size):
        for yAxis in range(location.y, location.y + size):
            for zAxis in range(location.z, location.z + size):
                randomInt = randint(0,7)
                singleBlockChange(Point(x=xAxis,y=yAxis,z=zAxis), acceptedBlocks[randomInt])

# function to transform blocks into input for the model to predict on
def transformInputForModel(inputBlocks, oneHotValues):

    # initialize the empty array of size (13 x 13 x 13) x 7 -> for one-hot
    threedArr2 = np.full(((13 * 13 * 13), 7), [1,0,0,0,0,0,0])

    # fill the array
    index = 0
    for block in inputBlocks.blocks:
        threedArr2[index] = oneHotValues[block.type]
        index += 1

    # flatten and reshape to correct format
    flattenedArray = threedArr2.flatten()
    finalArray = np.array(flattenedArray).reshape(HOUSE_HEIGHT,HOUSE_WIDTH,HOUSE_DEPTH,ACTION_SPACE)
    print (finalArray, finalArray.shape)
    return finalArray

# main function
if __name__ == '__main__':

    # clear the world
    clearMin = Point(x=-100, y=0, z=-50)
    clearMax = Point(x=100, y=100, z=50)
    worldReset(clearMin, clearMax)

    # generate noise block
    generateRandomNoiseBlock(Point(x=0,y=4,z=0), 6)

    # load the saved model
    loadedModel = tf.keras.models.load_model('paddedModels/prePaddedModel.h5')
    loadedModel.summary()

    # generate oneHotMapping
    oneHotValues = {}
    for block in acceptedBlocks:
        tempOneHot = [0] * (7)
        oneHotPosition = dict_one_hot_mapping[block]
        tempOneHot[oneHotPosition] = 1
        oneHotValues[block] = tempOneHot
    print(oneHotValues, "One hot encoded vectors")

    #######################  need to be fixed without hard-code ###############

    # go through all the noise structure blocks
    for xAxis in range(0, 6):
        for yAxis in range(4, 10):
            for zAxis in range(0, 6):

                # get the surrounding 13 x 13 x 13 blocks from the agent location at center
                minPosition = Point(x = xAxis - 6, y = yAxis - 6, z = zAxis - 6 )
                maxPosition = Point(x = xAxis + 6, y = yAxis + 6, z = zAxis + 6 )
                inputBlocks = client.readCube(Cube(min=minPosition, max=maxPosition))

                # transform the block data to model input
                inputData = transformInputForModel(inputBlocks, oneHotValues)

                '''
                # Predict the block to replace current position block using the model 
                predictions = loadedModel.predict(inputData)
                print("Predictions=", predictions)
                
                # Generate arg maxes for predictions
                predictedNewBlock = np.argmax(predictions, axis = 1)
                predictedNewBlock = predictedNewBlock[0]
                print("Predicted new block -> ", predictedNewBlock)
                '''

                predictedNewBlock = 2

                # dict to map ordinal values to cube types
                reverseValueMap = {0: 5, 1: 41, 2: 60, 3: 88, 4: 131, 5: 160, 6: 224}

                # replace the current location of agent with the predicted block
                singleBlockChange(Point(x=xAxis,y=yAxis,z=zAxis), reverseValueMap[predictedNewBlock])

                # copy agent action to show building being built
                singleBlockChange(Point(x=xAxis + 30,y=yAxis,z=zAxis), reverseValueMap[predictedNewBlock])
