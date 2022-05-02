import numpy as np

threedArr = np.full((6,6,6, 8), 5)
threedArr[0][1][2] = np.array([1, 0, 0, 0, 0, 0, 0, 0])
print(threedArr)