import numpy as np

# block types that we will allow
acceptedBlocks = [5, 41, 60, 88, 131, 160, 224]

# dictionary for one-hot mapping
dict_one_hot_mapping = {5: 0, 41: 1, 60: 2, 88: 3, 131: 4, 160: 5, 224: 6}


oneHotValues = {}
for block in acceptedBlocks:
    tempOneHot = [0] * (7)
    oneHotPosition = dict_one_hot_mapping[block]
    tempOneHot[oneHotPosition] = 1
    oneHotValues[block] = tempOneHot

blocks = [5, 41, 41, 88, 5, 88, 88, 5]
threedArr2 = np.full(((2 * 2 * 2), 7), [1,0,0,0,0,0,0])
index = 0
for block in blocks:
    threedArr2[index] = oneHotValues[block]
    index += 1

finalArray = threedArr2.flatten()
print(oneHotValues, "One hot encoded vectors")
print (threedArr2)
print (finalArray)