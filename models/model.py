import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import keras
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
import pickle

datas = pd.read_csv('datas/datas.csv')

X = datas.iloc[:, :-1].values
y = datas.iloc[:, 8].values

onehotencoder = OneHotEncoder()
X = onehotencoder.fit_transform(X).toarray()
x = pd.DataFrame(X)
x.drop([0, 14, 30, 44, 59, 71, 83, 98, 108], axis=1, inplace=True)


labelencoder_y = LabelEncoder()
y = labelencoder_y.fit_transform(y)
y = to_categorical(y)
Y = pd.DataFrame(y)


X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=0)


classifier = Sequential()
classifier.add(Dense(activation="relu", input_dim=101,
                     units=1, kernel_initializer="uniform"))
classifier.add(Dense(activation="relu", units=1, kernel_initializer="uniform"))
classifier.add(Dense(units=4, activation='softmax',
                     kernel_initializer='uniform'))
classifier.compile(
    optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

classifier.fit(X_train, y_train, batch_size=1, epochs=10)

# Normalement cette ligne permet d'enregistrer le modele sur le disque. La bibliothèque
pickle.dump(classifier, open('model.pkl', 'wb'))
# pickle permet de sérializer et déserialiser des objets structurés python
