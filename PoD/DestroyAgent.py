from copy import deepcopy
import grpc

import minecraft_pb2_grpc
from minecraft_pb2 import *

import random

channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

class PoDAgent:
    def __init__(self, minBound = Point(x=0,y=0,z=0), maxBound = Point(x=0,y=0,z=0)):
        
        #mute the block or not
        self.coinFlip = 80
        

        self.minBoundary = minBound
        self.maxBoundary = maxBound

        #start from minboundary to move the agent
        self.currPosition = deepcopy(self.minBoundary) 
        
        """
        45 = "CONCRETE"
        23 = "BRICK_BLOCK"
        217 = "STONE"
        """
        self.selectedTiles = [45, 23, 217]
        self.reachEnd = False

    # position argument needs a Point type instance, selectedType can be int or string
    def singleBlockChange (self, position, selectedType):
        print("position to change is: ", position)
        client.fillCube(FillCubeRequest(cube=Cube(
                        min = position,
                        max = position
                    ), type=selectedType))

    def getBlockType (self, position):
        blocks = client.readCube(Cube(min=position, max=position))

        return blocks.blocks[0].type
    
    def takeAction(self):
        #print ("action is taken")
        coinToss = random.randint(0, 100)
        print("agent min is: ", self.minBoundary)
        print("agent max is: ", self.maxBoundary)
        #currentX = self.minBoundary.x
        #currentY = self.minBoundary.y
        #currentZ = self.minBoundary.z
        #print("original location is: ", self.currPosition)

        action = self.getBlockType(self.currPosition)
        #proceed to take next step of destruction
        #Destruction traverse order is: z -> y -> x
        if coinToss <= self.coinFlip:
            #block will be changed to one of the type in tile Selection
            randomTile = random.randint(0, 2)
            tileChangeTo = self.selectedTiles[randomTile]
            self.singleBlockChange(self.currPosition, tileChangeTo)
        #after change or not move on to next target
        if self.currPosition.z + 1 < self.maxBoundary.z + 1:
            self.currPosition.z += 1
        elif self.currPosition.y + 1 < self.maxBoundary.y + 1:
            #print("z should reset")
            self.currPosition.z = self.minBoundary.z
            self.currPosition.y += 1
        elif self.currPosition.x + 1 < self.maxBoundary.x + 1:
            self.currPosition.z = self.minBoundary.z
            self.currPosition.y = self.minBoundary.y
            self.currPosition.x += 1
        #meet maxBoundary
        else:
            print("boundary reached")
            self.reachEnd = True
            return -1

        #print("new location is: ", self.currPosition)

         

        return action
    #take a random action then return the reversed action for record
    def takeRandomAction(self):
        coinToss = random.randint(0, 100)
        if coinToss <= self.coinFlip:
            randomTile = random.randint(0, 2)
            randomMove = random.randint(0, 6)
            # Make a random move while ensure it's within boundary
            # 0 means x - 1
            if randomMove == 0 and self.currPosition.x - 1 >= self.minBoundary.x:
                self.currPosition.x = self.currPosition.x - 1
                #record block change
                tileBeforeChange = self.getBlockType(self.currPosition)
                tileChangeTo = self.selectedTiles[randomTile]

                # make the move-to block change
                self.singleBlockChange(self.currPosition, tileChangeTo)
                move = Point(x=1,y=0,z=0)
                
                # action include reversed movement, tile type before change, tile type after change
                return (move, tileBeforeChange, tileChangeTo)

            elif randomMove == 1 and self.currPosition.x + 1 <= self.maxBoundary.x:
                self.currPosition.x = self.currPosition.x + 1
              
                tileBeforeChange = self.getBlockType(self.currPosition)
                tileChangeTo = self.selectedTiles[randomTile]

               
                self.singleBlockChange(self.currPosition, tileChangeTo)
                move = Point(x=1,y=0,z=0)
                
                
                return (move, tileBeforeChange, tileChangeTo)  

            elif randomMove == 2 and self.currPosition.y - 1 >= self.minBoundary.y:
                self.currPosition.y = self.currPosition.y - 1
                
                tileBeforeChange = self.getBlockType(self.currPosition)
                tileChangeTo = self.selectedTiles[randomTile]

                
                self.singleBlockChange(self.currPosition, tileChangeTo)
                move = Point(x=1,y=0,z=0)
                
                
                return (move, tileBeforeChange, tileChangeTo)

            elif randomMove == 3 and self.currPosition.y + 1 <= self.maxBoundary.y:
                self.currPosition.y = self.currPosition.y - 1
                
                tileBeforeChange = self.getBlockType(self.currPosition)
                tileChangeTo = self.selectedTiles[randomTile]

                
                self.singleBlockChange(self.currPosition, tileChangeTo)
                move = Point(x=1,y=0,z=0)
                
                
                return (move, tileBeforeChange, tileChangeTo) 

            elif randomMove == 4 and self.currPosition.z - 1 >= self.minBoundary.z:
                self.currPosition.z = self.currPosition.z - 1
              
                tileBeforeChange = self.getBlockType(self.currPosition)
                tileChangeTo = self.selectedTiles[randomTile]

              
                self.singleBlockChange(self.currPosition, tileChangeTo)
                move = Point(x=1,y=0,z=0)
                
                
                return (move, tileBeforeChange, tileChangeTo) 

            elif randomMove == 4 and self.currPosition.z + 1 <= self.maxBoundary.z:
                self.currPosition.z = self.currPosition.z + 1
                
                tileBeforeChange = self.getBlockType(self.currPosition)
                tileChangeTo = self.selectedTiles[randomTile]

               
                self.singleBlockChange(self.currPosition, tileChangeTo)
                move = Point(x=1,y=0,z=0)
                
                return (move, tileBeforeChange, tileChangeTo) 

        else:
            return

