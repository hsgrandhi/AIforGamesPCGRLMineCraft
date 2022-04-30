#won't work
#from turtle import position
import grpc

import minecraft_pb2_grpc
from minecraft_pb2 import *

import random
import numpy as np

from DestroyAgent import PoDAgent

import csv
import pandas as pd

channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

#TODO: fix min max, 
"""
*********** NOTICE **********
So as for the read in result, it traverse in this order for all Blocks.blocks[0] to [size]
first z will be first to move, then next on the list is y. Finally it's x.
Sothe output maybe a bit in quite a different order than expected
******************************
"""

def ravel_index(x, dims):
    i = 0
    for dim, j in zip(dims, x):
        i *= dim
        i += j
    return i


def singleBlockChange (position, selectedType):
        #print("position to change is: ", position)
        client.fillCube(FillCubeRequest(cube=Cube(
                        min = position,
                        max = position
                    ), type=selectedType))

def clearOut(minPoint, maxPoint, cubeType = "AIR"):
    client.fillCube(FillCubeRequest(  # Clear a 20x10x20 working area
        cube=Cube(
            min = minPoint,
            max = maxPoint
        ),
        type=cubeType
    ))
#by default grass and air are excluded, can also be diyed
def locateMinMax(minPoint, maxPoint, excludingType=[5, 93]):

    minX = maxPoint.x
    maxX = minPoint.x
    minY = maxPoint.y
    maxY = minPoint.y
    minZ = maxPoint.z
    maxZ = minPoint.z

    isBanned = False
    #print ("original min point is: ", minX, " ", minY, " ", minZ)
    #print ("original max point is: ", maxX, " ", maxY, " ", maxZ)
    allCubes = client.readCube(Cube(min=minPoint,max=maxPoint))

    for cube in allCubes.blocks:
        #print (cube.type)
        # 5 is the air block, 10 is bedrock
        # exclude air, bedrock, grass and dirt
        for type in excludingType:
            if cube.type == type:
                
                isBanned = True
                continue

        if not isBanned:    
            
            
            minX = min(cube.position.x, minX)
            minY = min(cube.position.y, minY)
            minZ = min(cube.position.z, minZ)

            maxX = max(cube.position.x, maxX)
            maxY = max(cube.position.y, maxY)
            maxZ = max(cube.position.z, maxZ)

        else:
            isBanned = False

        """
        if cube.type != 5 and cube.type != 10 and cube.type != 93 and cube.type != 60:
        #if cube.type != 5 and cube.type != 93:

            print("find the starting block")
            print("type is: ", cube.type)
            print("position is: ", cube.position)
            minX = min(cube.position.x, minX)
            minY = min(cube.position.y, minY)
            minZ = min(cube.position.z, minZ)

            maxX = max(cube.position.x, maxX)
            maxY = max(cube.position.y, maxY)
            maxZ = max(cube.position.z, maxZ)

        """
        
    outputTuple = (Point(x = minX, y = minY, z = minZ), 
                    Point(x = maxX, y = maxY, z = maxZ))
    return outputTuple

#giving accurate location of house, this will find all existing materials
#input: min boundary and max boundary
#output: a list of all existing tile within
def getExistingType(accurateMin, accurateMax):
    print("finding all block types of house")
    allCubes = client.readCube(Cube(min=accurateMin,max=accurateMax))
    output = []
    for cube in allCubes.blocks:
        if cube.type not in output:
            output.append(cube.type)
    return output

# ONLY use this function when accurate location of the house has been found
# input: accurate min coord and max coord and A LIST of block type 
# integer the house is made of, all other materials will be swapped with a random existing

def nbtProcessing(minCoord, maxCoord, includeBlocks = [5, 93]):

    allCubes = client.readCube(Cube(min=minCoord,max=maxCoord))
    passCheck = False

    for cube in allCubes.blocks:

        for include in includeBlocks:
            if cube.type == include:
                passCheck = True
                continue
        
        #edit the block if not within one of the block type, it will be swapped with one of the existing block type
        if not passCheck:
            #cube.type = includeBlocks[random.randint(0, len(includeBlocks) - 1)]
            singleBlockChange(cube.position, random.randint(0, len(includeBlocks) - 1))

        #else just reset the boolean and move on to next cube
        else:
            passCheck = False

#first will locate the house within the given boundary
#then it will be repainted at a different location while wipe out the original.
#input: current house location boundary, target min location (lowest point of the house)
def moveNBT(currMin, currMax, targetMin):
    print("nbt is moving")    
    #read in the current location house data first
    currentHouse = client.readCube(Cube(
        min=currMin,
        max=currMax
    ))
    blocksOnX = abs(currMax.x - currMin.x) + 1
    blocksOnY = abs(currMax.y - currMin.y) + 1
    blocksOnZ = abs(currMax.z - currMin.z) + 1
    clearOut(currMin, currMax, AIR)

    blockIndex = 0
    for i in range(targetMin.x, targetMin.x + blocksOnX):
        for j in range(targetMin.y, targetMin.y + blocksOnY):
            for k in range(targetMin.z, targetMin.z + blocksOnZ):
                singleBlockChange(Point(x=i,y=j,z=k), currentHouse.blocks[blockIndex].type)
                blockIndex += 1
                    



def generateStep(agent, minBound, maxBound):
    #print ("generating step")
    agentAction = agent.takeAction()
    blocks = client.readCube(Cube(
        min=agent.minBoundary,
        max=agent.maxBoundary
    ))
    output = (blocks, agentAction)
    return output

def transformStateActionToCSV(blocks, action, minPoint, maxPoint):
    # connect to the server
    # channel = grpc.insecure_channel('localhost:5001')
    # client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

    # get the boundries positions of the building
    
    # min is 40 2 10, max is 50 12 20
    # spawn center is 45, 7, 15
    print(minMax, "minMax")

    # read all the blocks in the range
    # blocks = client.readCube(Cube(
    #     min=Point(x=minMax[0].x, y=minMax[0].y, z=minMax[0].z),
    #     max=Point(x=minMax[1].x, y=minMax[1].y, z=minMax[1].z)
    # ))

    # create a 3D array with the max required dimensions, added + 1 to handle index errors
    threedArr = np.full((20,20,20), 5)
    print(threedArr.shape)
    for block in blocks.blocks:
        print("block is: ", block.type)
        #print("index is: ", block.position.x-41, block.position.y-3, block.position.z-11)
        threedArr[block.position.x-minPoint.x][block.position.y-minPoint.y][block.position.z-minPoint.z] = block.type
    print(threedArr)
    

    # flatten the array
    flattenedArray = np.stack(threedArr, axis=1).flatten()

    # add shape data to the flattened array
    # flattenedArray.append(threedArr.shape)
    # flattenedArray = np.append(flattenedArray, threedArr.shape)

    flattenedArray = np.append(flattenedArray, action)
    print(flattenedArray, flattenedArray.shape)
    with open("buildingData.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow(flattenedArray)

    # convert array into dataframe
    DF = pd.DataFrame(flattenedArray)
    
    # save the dataframe as a csv file
    DF.to_csv("data1.csv", index=False)

    

if __name__ == '__main__':

#x varies 50 - 53, z vaires -20 - 40, y varies 2 - 6
#load_coord=(50,10,1)
#the load coordinate function is have x, z, y instead

    accurateMin = Point(x=50, y=2, z=10)
    accurateMax = Point(x=53, y=6, z=15)

    #print(accurateLoc)
    excludingType = [5, 93, 10, 60]
    
    minMax = locateMinMax(Point(x=40, y=0, z=0), Point(x=60, y=10, z=20), excludingType)
    print ("minMax is: ", minMax)
    
    #minMax = [Point(x = 41, y = 3, z = 11), Point(x = 50, y = 12, z = 20)]
    
    currentBlocks = getExistingType(minMax[0], minMax[1])
    print("included blocks are: ", currentBlocks)
    
    #remove the TORCH block from the current blocks
    if TORCH in currentBlocks:
        currentBlocks.remove(TORCH)

    #use this processing function to swap out unwant blocks
    nbtProcessing(minMax[0], minMax[1], currentBlocks)

    """
    accurateLoc = client.readCube(Cube(
        min=accurateMin,
        max=accurateMax
    ))
    print(accurateLoc)
    """

    moveNBT(minMax[0], minMax[1], Point(x=55,y=2,z=20))
    
    """
    agent = PoDAgent(accurateMin, accurateMax)
    
   
    
    trainingData = []

    #debug
    
    while not agent.reachEnd:
        #agent.takeAction()
        step = generateStep(agent, minBound, maxBound)
        trainingData.append(step, accurateMin, accurateMax)
        transformStateActionToCSV(step[0], step[1])

    

    print (trainingData)
    """



    #print(trainingData)
   
    
   
    #example syntax to use the readCube result, Blocks type obj
    #print (blocks.blocks[0].type)



    #read func test (flying machine loc)
    #minPoint = Point(x=1, y=5, z=-4)
    #maxPoint = Point(x=1, y=6, z=1)

    #output = []
    #output = destroyer(minPoint, maxPoint)
    #print(output)
    #readBlocks = readSingleCubes(minPoint, maxPoint)

    #print("below is single read result")
    #print(readBlocks[0])   


