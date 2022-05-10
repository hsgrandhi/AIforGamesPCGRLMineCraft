import grpc

import minecraft_pb2_grpc
from minecraft_pb2 import *

import random
import numpy as np

from DestroyAgent import PoDAgent

import csv
import pandas as pd
from pandas import *

channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

df_firstn = pd.read_csv('buildingData0.csv', nrows=216)
endState = df_firstn.iloc[0].to_numpy()
print(endState, len(endState), "1")
endState = endState[:-1]
print(endState, len(endState), "2")
reshapedEndState = np.reshape(endState, (6,6,6))
print(reshapedEndState)

blocks = []
for xAxis in range(0, 6):
    for yAxis in range(0,6):
        for zAxis in range(0, 6):
            tempBlock = Block(position=Point(x=xAxis, y=yAxis + 4, z=zAxis), type=reshapedEndState[xAxis][yAxis][zAxis])
            print(tempBlock)
            blocks.append(tempBlock)

client.spawnBlocks(Blocks(blocks=blocks)) 

for i in range(214, 0, -1):
    currentRow = df_firstn.iloc[i].to_numpy()
    currentAction = currentRow[-1]
    print(currentAction)