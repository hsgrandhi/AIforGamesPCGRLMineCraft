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
        self.currPosition = self.minBoundary
        
        """
        45 = "CONCRETE"
        23 = "BRICK_BLOCK"
        217 = "STONE"
        """
        self.selectedTiles = [45, 23, 217]


    # position argument needs a Point type instance, selectedType can be int or string
    def singleBlockChange (self, position, selectedType):
        client.fillCube(FillCubeRequest(cube=Cube(
                        min = position,
                        max = position
                    ), type=selectedType))

    def getBlockType (self, position):
        blocks = client.readCube(Cube(min=position, max=position))

        return blocks.blocks[0].type
    
    # take a random action then return the reversed action for record
    def takeAction(self):
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
