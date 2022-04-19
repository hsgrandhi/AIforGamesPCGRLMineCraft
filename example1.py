import grpc
import minecraft_pb2_grpc as minecraft_pb2_grpc
from minecraft_pb2 import *
import numpy as np
import numpy as np
from IPython.display import clear_output



channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)
# base_nbt_path = {path to nbts}


# load_file = "../dataset/jsons/apartment_complex.json"


# base_nbt_path = '../dataset/nbts/'
# nbt_path = "{}/mini_castle.nbt".format(base_nbt_path)

# blocks, unique_vals, target, color_dict, unique_val_dict = MinecraftClient.load_entity("Apartment", nbt_path=nbt_path, load_coord=(50,10,1))



client.fillCube(FillCubeRequest(  # Clear a 20x10x20 working area
    cube=Cube(
        min=Point(x=-10, y=4, z=-10),
        max=Point(x=10, y=14, z=10)
    ),
    type=AIR
))
# client.spawnBlocks(Blocks(blocks=[  # Spawn a flying machine
#     # Lower layer
#     Block(position=Point(x=1, y=5, z=1), type=PISTON, orientation=NORTH),
#     Block(position=Point(x=1, y=5, z=0), type=SLIME, orientation=NORTH),
#     Block(position=Point(x=1, y=5, z=-1), type=STICKY_PISTON, orientation=SOUTH),
#     Block(position=Point(x=1, y=5, z=-2), type=PISTON, orientation=NORTH),
#     Block(position=Point(x=1, y=5, z=-4), type=SLIME, orientation=NORTH),
#     # Upper layer
#     Block(position=Point(x=1, y=6, z=0), type=REDSTONE_BLOCK, orientation=NORTH),
#     Block(position=Point(x=1, y=6, z=-4), type=REDSTONE_BLOCK, orientation=NORTH),
#     # Activate
#     Block(position=Point(x=1, y=6, z=-1), type=QUARTZ_BLOCK, orientation=NORTH),
# ]))


blocks = client.readCube(Cube(
    min=Point(x=-10, y=4, z=-10),
    max=Point(x=10, y=14, z=10)
))

# print(blocks)