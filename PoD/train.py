import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint
import pandas as pd
import numpy as np
from keras.utils import np_utils
import sys

# Set variables
HOUSE_WIDTH = 6
HOUSE_HEIGHT = 6
HOUSE_DEPTH = 6
TARGET_COL = 216
ACTION_SPACE = 8
DATA_FILE = "buildingData2.csv"
MODEL_PATH = "models"


value_map = {5: 0, 41: 1, 224: 2, 60: 3, 160: 4, 131: 5, 88: 6}
df = pd.read_csv(DATA_FILE, header=None)
print(f"df shape {len(df)} rows {len(df.iloc[0])} cols")
print(f"df: \n{df.head()}\n\n")

df = df.sample(frac=1).reset_index(drop=True)
y = df.iloc[:, -1].values
df.drop(TARGET_COL, axis=1, inplace=True)
y = y.astype('int32')

# Map block values to ordinal via value_map
for row_idx in range(len(df)):
    cols = df.iloc[row_idx].values
    for col_idx in range(len(cols)):
        df.iloc[row_idx,col_idx] = value_map.get(cols[col_idx], 7)
    y[row_idx] = value_map.get(y[row_idx], 7)

X = []
# Convert df to onehot
for row_idx in range(len(df)):
    cols = df.iloc[row_idx].values
    new_row = []
    for col_idx in range(len(cols)):
        new_onehot = [0]*8
        new_onehot[df.iloc[row_idx, col_idx]] = 1
        new_row.append(new_onehot)
    new_row = np.array(new_row).reshape(HOUSE_HEIGHT,HOUSE_WIDTH,HOUSE_DEPTH,ACTION_SPACE)
    X.append(new_row)

    y[row_idx] = value_map.get(y[row_idx], 7)

# convert y to onehot
y = np_utils.to_categorical(y)
X = np.array(X)

# Define model
model = tf.keras.models.Sequential([
        tf.keras.layers.Conv3D(128, 3, activation='relu',
                               input_shape=(HOUSE_HEIGHT,HOUSE_WIDTH,HOUSE_DEPTH,ACTION_SPACE)),
        tf.keras.layers.MaxPooling3D(2),
        tf.keras.layers.Conv3D(128, 3, activation='relu', padding="SAME"),
        tf.keras.layers.Conv3D(256, 3, activation='relu', padding="SAME"),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(8, activation='softmax')
    ])

model.summary()

model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=[tf.keras.metrics.CategoricalAccuracy()])
mcp_save = ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor='categorical_accuracy', mode='max')
history = model.fit(X, y, epochs=500, steps_per_epoch=64, verbose=2, callbacks=[mcp_save])


