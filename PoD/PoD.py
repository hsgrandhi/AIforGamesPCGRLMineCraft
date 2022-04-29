#won't work
#from turtle import position
import grpc

import minecraft_pb2_grpc
from minecraft_pb2 import *

import random
import numpy as np

from DestroyAgent import PoDAgent

import csv

channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

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

#clear out game world, moved platform etc
def clearOut(minPoint, maxPoint):
    client.fillCube(FillCubeRequest(  # Clear a 20x10x20 working area
        cube=Cube(
            min = minPoint,
            max = maxPoint
        ),
        type=AIR
    ))

#read cubes n store in a list for easier access
def readSingleCubes(minPoint, maxPoint):
    outputBlock = []
    tempRead = Blocks()
    for i in range(minPoint.x, maxPoint.x + 1):
        for j in range(minPoint.y, maxPoint.y + 1):
            for k in range(minPoint.z, maxPoint.z + 1):
                outputBlock.append(client.readCube(Cube(
                    min = Point(x=i, y=j, z=k),
                    max = Point(x=i, y=j, z=k)
                )))
    return outputBlock 

def spawnFlyingMachine():
    client.spawnBlocks(Blocks(blocks=[  # Spawn a flying machine
        # Lower layer
        Block(position=Point(x=1, y=5, z=1), type=CLAY, orientation=NORTH),
        Block(position=Point(x=1, y=5, z=0), type=GLASS, orientation=NORTH),
        Block(position=Point(x=1, y=5, z=-1), type=BRICK_BLOCK, orientation=SOUTH),
        Block(position=Point(x=1, y=5, z=-2), type=STONE, orientation=NORTH),
        Block(position=Point(x=1, y=5, z=-4), type=SLIME, orientation=NORTH),
        # Upper layer
        Block(position=Point(x=1, y=6, z=0), type=REDSTONE_BLOCK, orientation=NORTH),
        Block(position=Point(x=1, y=6, z=-4), type=REDSTONE_BLOCK, orientation=NORTH),
        # Activate
        Block(position=Point(x=1, y=6, z=-1), type=QUARTZ_BLOCK, orientation=NORTH),
        
    ]))

def locateMinMax(minPoint, maxPoint):

    minX = maxPoint.x
    maxX = minPoint.x
    minY = maxPoint.y
    maxY = minPoint.y
    minZ = maxPoint.z
    maxZ = minPoint.z

    #print ("original min point is: ", minX, " ", minY, " ", minZ)
    #print ("original max point is: ", maxX, " ", maxY, " ", maxZ)
    allCubes = client.readCube(Cube(min=minPoint,max=maxPoint))

    for cube in allCubes.blocks:
        #print (cube.type)
        # 5 is the air block, 10 is bedrock
        # exclude air, bedrock and dirt
        if cube.type != 5 and cube.type != 10 and cube.type != 93 and cube.type != 60:
        #if cube.type != 5 and cube.type != 93:
        
            minX = min(cube.position.x, minX)
            minY = min(cube.position.y, minY)
            minZ = min(cube.position.z, minZ)

            maxX = max(cube.position.x, maxX)
            maxY = max(cube.position.y, maxY)
            maxZ = max(cube.position.z, maxZ)
        


    outputTuple = (Point(x = minX, y = minY, z = minZ), 
                    Point(x = maxX, y = maxY, z = maxZ))
    return outputTuple

def generateStep(agent):
    #print ("generating step")
    agentAction = agent.takeAction()
    blocks = client.readCube(Cube(
        min=agent.minBoundary,
        max=agent.maxBoundary
    ))
    output = (blocks, agentAction)
    return output


    

"""
#before switching, the range for blocks need to be set.
#same as fill cube but instead given a chance to fill also fill type is random.
def destroyerMK1(minPoint, maxPoint):
    print("destroyer is running")
    outputList = []
    for i in range (minPoint.x, maxPoint.x + 1):
        for j in range (minPoint.y, maxPoint.y + 1):
            for k in range (minPoint.z, maxPoint.z):
                #hit the chance and changing the block at this spot.
                if random.randint(0, 100) < 80:
                    randomType = random.randint(6, 253)
                    #read the block at the location and obtaining this current info
                    currBlock = client.readCube(Cube(
                    min = Point(x=i, y=j, z=k),
                    max = Point(x=i, y=j, z=k)))
                    currType = currBlock.blocks[0].type
                    location = Point(x=i, y=j, z=k)
                    #create a tuple contains original type index and position
                    #With addition data added as the change to block index
                    #in the order of 1.location, 2.previous block type, 3.current block type
                    tempTuple = (location, currType, randomType)
                    outputList.append(tempTuple)
                    #write over the position using fill
                    client.fillCube(FillCubeRequest(cube=Cube(
                        min = Point(x=i, y=j, z=k),
                        max = Point(x=i, y=j, z=k)
                    ),
                    type=randomType))

    return outputList
    

"""

if __name__ == '__main__':

   
    


    #These are the tile that will be used to do the random swap
    #Using 3 at top
    

   
    
#x varies 50 - 53, z vaires -20 - 40, y varies 2 - 6
#load_coord=(50,10,1)
#the load coordinate function is have x, z, y instead

    accurateMin = Point(x=50, y=2, z=10)
    accurateMax = Point(x=53, y=6, z=15)

    accurateLoc = client.readCube(Cube(
        min=accurateMin,
        max=accurateMax
    ))
    #print(accurateLoc)
    
    minMax = locateMinMax(accurateMin, accurateMax)
    #print ("minMax is: ", minMax)
    

  
    
    
    
    agent = PoDAgent(minMax[0], minMax[1])
    
   
    
    trainingData = []

    #debug
    
    while not agent.reachEnd:
        #agent.takeAction()
        trainingData.append(generateStep(agent))

    

    print (trainingData)

    """
    #print(len(trainingData[0][0].blocks) + 2)
    outputRow = np.zeros(len(trainingData[0][0].blocks) + 2)
    output = []


    
    
    #print(outputRow[len(trainingData[0][0].blocks) + 1])

    for data in trainingData:
        for i in range (len(data[0].blocks)):
            
            temp = data[0].blocks[i].type
            outputRow[i] = temp
        
        outputRow[len(data[0].blocks) + 1] = (data[1])
        
        output.append(outputRow)

        print (output)

    
    
    with open("out.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(output)
   
   
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


