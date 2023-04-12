import os
# Make TensorFlow logs less verbose
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import flwr as fl
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D,Flatten,Dense
from tensorflow.keras.optimizers import SGD
import numpy as np
import pandas as pd
import ray
from matplotlib import pyplot as plt

from src.utils import INPUT_SHAPE, NUM_CLASSES, BATCH_SIZE
from src.utils import define_strategy, weighted_average
from src.train import train_model_federative, train_model_without_fed
from src.data import load_data

if __name__ == "__main__":
    # load data
    (x_train, y_train), (x_test, y_test) = load_data()

    strategy = define_strategy()

    # train model
    for epochs in range(10, 25, 5):
        print(f"Training model with {epochs} epochs")

        print("Training model without federative learning")
        train_model_without_fed(x_train, y_train, epochs)

        print("Training model with federative learning")
        train_model_federative(epochs, strategy)