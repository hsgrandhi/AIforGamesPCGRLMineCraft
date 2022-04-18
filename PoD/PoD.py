#won't work
#from turtle import position
import grpc

import minecraft_pb2_grpc
from minecraft_pb2 import *

import random
import numpy as np

channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)


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

"""
#use together with the block read function
def sizeFinder(readInBlocks, minPoint, maxPoint):
    xmin = -1000
    xmax = 1000
    ymin = -1000
    ymax = 1000
    zmin = -1000
    zmax = 1000
    
    blocks = client.readCube(Cube(
        min=Point(x=1, y=5, z=-4),
        max=Point(x=1, y=6, z=1)
    ))
    return
"""


#before switching, the range for blocks need to be set.
#same as fill cube but instead given a chance to fill also fill type is random.
def destroyer(minPoint, maxPoint):
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
    

if __name__ == '__main__':

    #clear out a 1000 * 18 * 1000 area
    clearMin = Point(x=-500, y=4, z=-500)
    clearMax = Point(x=500, y=14, z=500)
    clearOut(clearMin, clearMax)
    


    #These are the tile that will be used to do the random swap
    #Using 3 at top
    

   
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

        
    blocks = client.readCube(Cube(
        min=Point(x=1, y=5, z=-4),
        max=Point(x=1, y=6, z=1)
    ))

    testPoint = Point(x = 0, y=0, z=0)
    testPoint.x = testPoint.x - 5
    print(testPoint.x)
    #example syntax to use the readCube result, Blocks type obj
    print (blocks.blocks[0].type)



    #read func test (flying machine loc)
    #minPoint = Point(x=1, y=5, z=-4)
    #maxPoint = Point(x=1, y=6, z=1)

    #output = []
    #output = destroyer(minPoint, maxPoint)
    #print(output)
    #readBlocks = readSingleCubes(minPoint, maxPoint)

    #print("below is single read result")
    #print(readBlocks[0])   


