import flwr as fl
import numpy as np

from src.data import load_data
from src.models import define_model
from src.utils import INPUT_SHAPE, NUM_CLASSES, NUM_CLIENTS

class FlowerClient(fl.client.NumPyClient):
    def __init__(self, model, x_train, y_train, x_test, y_test) -> None:
        self.model = model
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test
        self.y_test = y_test

    def get_parameters(self, config):
        return self.model.get_weights()

    def fit(self, parameters, config):
        self.model.set_weights(parameters)
        self.model.fit(self.x_train, self.y_train, epochs=1, verbose=2)
        return self.model.get_weights(), len(self.x_train), {}

    def evaluate(self, parameters, config):
        self.model.set_weights(parameters)
        loss, acc = self.model.evaluate(self.x_test, self.y_test, verbose=2)
        return loss, len(self.x_test), {"accuracy": acc}

def flower_client_model(cid: str) -> fl.client.Client:   
    (x_train, y_train), (x_test, y_test) = load_data()
    sample_size_train = int((1/NUM_CLIENTS)*len(x_train))
    sample_size_test = int((1/NUM_CLIENTS)*len(x_test))

    idx_train = np.random.choice(np.arange(len(x_train)), sample_size_train, replace=False)
    x_train = x_train[idx_train]
    y_train = y_train.numpy()[idx_train]

    idx_test = np.random.choice(np.arange(len(x_test)), sample_size_test, replace=False)
    x_test = x_test[idx_test]
    y_test = y_test.numpy()[idx_test]

    model = define_model(INPUT_SHAPE, NUM_CLASSES)

    # Create and return client
    return FlowerClient(model, x_train, y_train, x_test, y_test)