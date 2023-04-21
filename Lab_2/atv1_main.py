import os
# Make TensorFlow logs less verbose
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from src.utils import define_strategy
from src.train import train_model_federated, train_model_without_fed
from src.data import load_data

if __name__ == "__main__":
    # load data
    (x_train, y_train), (x_test, y_test) = load_data()

    strategy = define_strategy()

    # train model
    for epochs in range(10, 25, 5):
        print(f"Training model with {epochs} epochs")

        print("Training model without federated learning")
        train_model_without_fed(x_train, y_train, epochs)

        print("Training model with federated learning")
        train_model_federated(epochs, strategy)