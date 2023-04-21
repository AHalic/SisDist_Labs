import flwr as fl
import pandas as pd
import os
from src.utils import weighted_average

if __name__ == "__main__":
    # Start Flower server localhost
    
    MIN_NUM_CLIENTS = 5
    NUM_CLIENTS = 6

    strategy = fl.server.strategy.FedAvg(
            fraction_fit=0.9,  
            fraction_evaluate=1,  
            min_fit_clients=MIN_NUM_CLIENTS,  
            min_evaluate_clients=MIN_NUM_CLIENTS,  
            min_available_clients=int(NUM_CLIENTS * 0.9),  
            evaluate_metrics_aggregation_fn=weighted_average
        )
    

    for round in [2, 5, 10, 20, 40]:
        history = fl.server.start_server(server_address='localhost:8080',
                           config=fl.server.ServerConfig(num_rounds=round),
                            strategy=strategy)
        # save to df
            # save history accuracy
        print(history)
        df = pd.DataFrame(history.metrics_distributed["accuracy"])
        df = df.drop(columns=[0])
        df.columns = ["accuracy"]

        if not os.path.exists('results_atv2'):
            os.makedirs('results_atv2')
        df.to_csv(os.path.join('results_atv2', f"accuracy_per_round_{round}.csv"), index=False)
            
    
    print(history)