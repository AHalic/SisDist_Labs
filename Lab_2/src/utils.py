import flwr as fl

# global variables
INPUT_SHAPE = (28, 28, 1)
NUM_CLASSES = 10
BATCH_SIZE = 64
NUM_CLIENTS = 10
MIN_NUM_CLIENTS = 9


def weighted_average(metrics):
    # Multiply accuracy of each client by number of examples used
    acc = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    results = {"accuracy": sum(acc) / sum(examples)}
    return results

def define_strategy():
    print("Strategy: FedAvg")
    print("Fraction fit: 0.9")
    print("Fraction evaluate: 1")
    print("Min fit clients:", NUM_CLIENTS)
    print("Min evaluate clients:", NUM_CLIENTS)
    print("Min available clients:", int(NUM_CLIENTS * 0.9))
    print("Evaluate metrics aggregation fn: weighted_average\n")

    return fl.server.strategy.FedAvg(
            fraction_fit=0.9,  
            fraction_evaluate=1,  
            min_fit_clients=MIN_NUM_CLIENTS,  
            min_evaluate_clients=MIN_NUM_CLIENTS,  
            min_available_clients=int(NUM_CLIENTS * 0.9),  
            evaluate_metrics_aggregation_fn=weighted_average
        )
