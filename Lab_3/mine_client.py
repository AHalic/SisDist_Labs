import grpc
import mine_grpc_pb2
import mine_grpc_pb2_grpc
import pybreaker

breaker = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=2)

@breaker
def run(client, item):
    pass

@breaker
def connect():
    pass

if __name__ == '__main__':
    connect()