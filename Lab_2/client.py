import flwr as fl
from src.flower_client import flower_client_model

if __name__ == "__main__":
    print("Starting Flower client...")
    try:
        fl.client.start_numpy_client(
            server_address="localhost:8080",
            client=flower_client_model())
    except Exception as e:
        print(e)
        print("ERROR: Failed to start Flower client")
        print("ERROR: Please make sure that the Flower server is running")