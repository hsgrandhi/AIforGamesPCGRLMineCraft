from copy import deepcopy
import grpc

import minecraft_pb2_grpc
from minecraft_pb2 import *
import numpy as np
import csv

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
        
      
        # self.selectedTiles = [45, 23, 217]
        self.selectedTiles = [5, 41, 131, 160, 88, 224, 60]
        self.reachEnd = False


    def clearOut(self, minPoint, maxPoint, cubeType = "AIR"):
        client.fillCube(FillCubeRequest(cube=Cube(min = minPoint,max = maxPoint),type=cubeType))

    # position argument needs a Point type instance, selectedType can be int or string
    def singleBlockChange (self, position, selectedType):
        #print("position to change is: ", position)
        client.fillCube(FillCubeRequest(cube=Cube(
                        min = position,
                        max = position
                    ), type=selectedType))

    def getBlockType (self, position):
        blocks = client.readCube(Cube(min=position, max=position))

        return blocks.blocks[0].type
    

    def takeActionWPadding(self):
        #print ("action is taken")
        self.generatePadding()
        coinToss = random.randint(0, 100)
        
        
        #action, which is the original tile type before change been made is recorded here
        action = self.getBlockType(self.currPosition)
        #proceed to take next step of destruction
        #Destruction traverse order is: z -> y -> x
        if coinToss <= self.coinFlip:
            #block will be changed to one of the type in tile Selection
            randomTile = random.randint(0, 7)
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
            return action

        #print("new location is: ", self.currPosition)

         

        return action

    def takeAction(self):
        #print ("action is taken")
        
        coinToss = random.randint(0, 100)
        
        
        #action, which is the original tile type before change been made is recorded here
        action = self.getBlockType(self.currPosition)
        #proceed to take next step of destruction
        #Destruction traverse order is: z -> y -> x
        if coinToss <= self.coinFlip:
            #block will be changed to one of the type in tile Selection
            randomTile = random.randint(0, 6)
            tileChangeTo = self.selectedTiles[randomTile]
            self.singleBlockChange(self.currPosition, tileChangeTo)
        

        #print("new location is: ", self.currPosition)

         

        return action

    def makeAMove(self):
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
            return 



    def generatePadding(self, location, size, material):
        #print("generate padding block")
        min = Point(x=location.x - size.x,y=location.y - size.y,z=location.z - size.z)
        max = Point(x=location.x + size.x,y=location.y + size.y,z=location.z + size.z)
        
        self.clearOut(min, max, material)
        output = [min, max]
        return output     

    def transformStateActionToCSV(self, blocks, action, minPoint, acceptedBlocks, fileName = "buildingData0.csv"):
        secondFileName = fileName
        threedArr2 = np.full((13 * 13 * 13), 5)
        #print(threedArr2.shape)
        index = 0
        for block in blocks.blocks:
            #print("index is: ", block.position.x-41, block.position.y-3, block.position.z-11)
            # threedArr[block.position.x-minPoint.x][block.position.y-minPoint.y][block.position.z-minPoint.z] = block.type
            threedArr2[index] = block.type
            index += 1
        #print(threedArr)
        # flatten the array
        flattenedArray2 = np.append(threedArr2, action)
        
        with open(secondFileName, "a", newline='') as f2:
            writer = csv.writer(f2)
            writer.writerow(flattenedArray2)

    # This is equal to combining the genStep together in one packet
    def fastAction(self, paddingSize, acceptedBlocks, fileName, result = []):
        self.currPosition = self.minBoundary
        currHouse = client.readCube(Cube(min=self.minBoundary,max=self.maxBoundary))
        action = -1
        
        
        for block in currHouse.blocks:
            print("agent location is: ", self.currPosition)
            action = block.type
            coinToss = random.randint(0, 100)
        
            if coinToss <= self.coinFlip:
                #block will be changed to one of the type in tile Selection
                randomTile = random.randint(0, 6)
                block.type = self.selectedTiles[randomTile]


            tempMinMax = self.generatePadding(self.currPosition, paddingSize, GLASS)
            self.clearOut(self.minBoundary, self.maxBoundary, AIR)
            client.spawnBlocks(currHouse)
            finalResult = client.readCube(Cube(min=tempMinMax[0],max=tempMinMax[1]))

            result.append(finalResult)

            output = (finalResult, action)
            self.transformStateActionToCSV(output[0], output[1], self.minBoundary, acceptedBlocks, fileName)
            if not self.reachEnd:
                self.makeAMove()
        


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



class buildAgent:
    def __init__(self, minBound = Point(x=0,y=0,z=0), maxBound = Point(x=0,y=0,z=0)):
        
        #mute the block or not
        
        

        self.minBoundary = minBound
        self.maxBoundary = maxBound

        #start from minboundary to move the agent
        self.currPosition = deepcopy(self.maxBoundary) 
        
        
      
        self.reachEnd = False

    # position argument needs a Point type instance, selectedType can be int or string
    def singleBlockChange (self, position, selectedType):
        #print("position to change is: ", position)
        client.fillCube(FillCubeRequest(cube=Cube(
                        min = position,
                        max = position
                    ), type=selectedType))

    def getBlockType (self, position):
        blocks = client.readCube(Cube(min=position, max=position))

        return blocks.blocks[0].type
    
    def repair(self, action):
        #print ("action is taken")
     
        
        
        #action, which is the original tile type before change been made is recorded here
        
        #proceed to take next step of destruction
        #Destruction traverse order is: z -> y -> x
       #TODO: boundary is off by 1 for everything
        
        tileChangeTo = action
        self.singleBlockChange(self.currPosition, tileChangeTo)
        #after change or not move on to next target
        if self.currPosition.z - 1 > self.minBoundary.z - 1:
            self.currPosition.z -= 1
        elif self.currPosition.y - 1 > self.minBoundary.y - 1:
            
            self.currPosition.z = self.maxBoundary.z
            self.currPosition.y -= 1
        elif self.currPosition.x - 1 > self.minBoundary.x - 1:
            
            self.currPosition.z = self.maxBoundary.z
            self.currPosition.y = self.maxBoundary.y
            self.currPosition.x -= 1
        #meet maxBoundary
        else:
            print("boundary reached")
            self.reachEnd = True
            return action

        #print("new location is: ", self.currPosition)

         

        return action
    #take a random action then return the reversed action for record
    

