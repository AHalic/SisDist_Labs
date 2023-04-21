import flwr as fl
import pandas as pd
import os

from src.flower_client import flower_client_model
from src.models import define_model
from src.utils import INPUT_SHAPE, NUM_CLASSES, BATCH_SIZE, NUM_CLIENTS

def train_model_federated(epochs, strategy):
    print("starting simulation")
    
    # Start simulation
    history = fl.simulation.start_simulation(
        client_fn=flower_client_model,
        num_clients=NUM_CLIENTS,
        config=fl.server.ServerConfig(num_rounds=epochs),
        strategy=strategy,   
    )

    # save history accuracy
    print(history.metrics_distributed["accuracy"])
    df = pd.DataFrame(history.metrics_distributed["accuracy"])
    df = df.drop(columns=[0])
    df.columns = ["accuracy"]
  
    df.to_csv(os.path.join("results", f"accuracy_per_epoch_fed_{epochs}.csv"), index=False)

def train_model_without_fed(x_train, y_train, epochs):
    # define model
    model = define_model(INPUT_SHAPE, NUM_CLASSES)

    # fit model
    history = model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=epochs, validation_split=0.1)

    # save to df
    accuracy_per_epoch = history.history['accuracy']
    df = pd.DataFrame(accuracy_per_epoch)
    df.columns = ["accuracy"]
    df.to_csv(os.path.join('results', f"accuracy_per_epoch_no_fed_{epochs}.csv"), index=False)
