from random import randint
import grpc
import numpy as np
import pandas as pd
from PoD import singleBlockChange
import tensorflow as tf

import minecraft_pb2_grpc
from minecraft_pb2 import *
from PoD import locateMinMax

# Set variables
HOUSE_WIDTH = 6
HOUSE_HEIGHT = 6
HOUSE_DEPTH = 6
TARGET_COL = 216
ACTION_SPACE = 8

# connect to the server
channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

# block types that we will allow
acceptedBlocks = [5, 41, 60, 88, 131, 160, 224, 247]

# function to generate a random noise block of size n
def generateRandomNoiseBlock(location, size):
    for xAxis in range(location.x, location.x + size):
        for yAxis in range(location.y, location.y + size):
            for zAxis in range(location.z, location.z + size):
                randomInt = randint(0,7)
                singleBlockChange(Point(x=xAxis,y=yAxis,z=zAxis), acceptedBlocks[randomInt])

# make the agent take a step
def generateStep(agent):
    agentAction = agent.takeAction()
    blocks = client.readCube(Cube(
        min=agent.minBoundary,
        max=agent.maxBoundary
    ))
    return blocks

'''
# function to transform blocks into input for the model to predict on
def oneHotTransformInput(inputBlocks, action, minPoint, acceptedBlocks, dictForOneHotMapping):
    # dict to map cube types to ordinal values
    value_map = {5: 0, 41: 1, 60: 2, 88: 3, 131: 4, 160: 5, 224: 6, 247: 7}
    threedArr = np.full((6,6,6), 5)

    for block in inputBlocks.blocks:
        threedArr[block.position.x-minPoint.x][block.position.y-minPoint.y][block.position.z-minPoint.z] = block.type

    # flatten the array
    flattenedArray = np.stack(threedArr, axis=1).flatten()
    flattenedArray = np.append(flattenedArray, action)

    df = pd.DataFrame(flattenedArray)

    # Map block values to ordinal via value_map
    for row_idx in range(len(df)):
        # cols = df.iloc[row_idx].values
        # for col_idx in range(len(cols)):
        df.iloc[row_idx] = value_map.get(cols[col_idx], 8)
        # y[row_idx] = value_map.get(y[row_idx], 8)

    # Convert df to onehot

    X = []
    for row_idx in range(len(df)):
        cols = df.iloc[row_idx].values
        new_row = []
        for col_idx in range(len(cols)):
            new_onehot = [0]*8
            new_onehot[df.iloc[row_idx, col_idx]] = 1
            new_row.append(new_onehot)
        new_row = np.array(new_row).reshape(HOUSE_HEIGHT,HOUSE_WIDTH,HOUSE_DEPTH,ACTION_SPACE)
        X.append(new_row)

        # y[row_idx] = value_map.get(y[row_idx], 8)
    X = np.array(X)
    return X
'''

# main function
if __name__ == '__main__':

    # generate noise block
    generateRandomNoiseBlock(Point(x=0,y=4,z=0), 6)

    # load the saved model
    model = tf.keras.models.load_model('models/saved_model')
    model.summary()

'''
    # Initialize the builderAgent to start at the noise block
    agent = builderAgent(location)

    # agent will move through the noise block
    for loop to move the agent across the noise block:

        inputBlocks = generateStep(agent)

        # one-hot encode the inputBlocks to feed to model 

        oneHotEncodedInputBlocks = oneHotTransformInput(inputBlocks)
        # Predict the block to replace current position block using the model 
        predictedNewBlock = model.predict(oneHotEncodedInputBlocks)

        # replace the current location of agent with the predicted block
        singleBlockChange(Point(x=x,y=y,z=z), predictedNewBlock)

        # copy agent action to show building being built
        singleBlockChange(Point(x=x + 10,y=y,z=z), predictedNewBlock)
'''