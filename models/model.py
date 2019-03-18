# -*- coding: utf-8 -*-
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

dataset = pd.read_csv('datas/donnees.csv')

categoricals = []
y = dataset.iloc[:, 7].values
dependent_variable = 'Personnalite'


for col, col_type in dataset.dtypes.iteritems():
    if col_type == 'O':
        categoricals.append(col)

df_ohe = pd.get_dummies(dataset, columns=categoricals, dummy_na=True)

x = df_ohe[df_ohe.columns.difference([dependent_variable])]

labelencoder_y = LabelEncoder()
y = labelencoder_y.fit_transform(y)
y = to_categorical(y)
y = pd.DataFrame(y)

X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=0)

classifier = Sequential()
classifier.add(Dense(activation="relu", input_dim=113,
                     units=51, kernel_initializer="uniform"))
classifier.add(Dense(activation="relu", units=51,
                     kernel_initializer="uniform"))
classifier.add(Dense(units=4, activation='softmax',
                     kernel_initializer='uniform'))
classifier.compile(
    optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])
classifier.fit(X_train, y_train, batch_size=1, nb_epoch=10)

y_pred = classifier.predict(X_test)
test_loss, test_acc = classifier.evaluate(X_test, y_test)
pickle.dump(classifier, open('model.pkl', 'wb'))
model_columns = list(x.columns)
pickle.dump(model_columns, open('model_columns.pkl', 'wb'))
