import grpc
import mine_grpc_pb2
import mine_grpc_pb2_grpc
import pybreaker
import random
import threading
import hashlib
from math import inf
import sys

global CLIENT_ID 

CLIENT_ID = random.randint(1, 100)

StatusEnum = {
    0: 'Desafio Resolvido',
    1: 'Desafio Pendente',
    -1: 'Desafio Inválido',
}

breaker = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=2)

def getTransactionId(client):
    res = client.getTransactionId(mine_grpc_pb2.void())
    print('id da transação: ', res.result)
    return res.result

def getChallenge(client, transaction_id=None): 
    if transaction_id is None:
        transaction_id = int(input('Digite o id da transação desejada: '))
    res = client.getChallenge(mine_grpc_pb2.transactionId(transactionId=transaction_id))

    if res.result == -1:
        print('Desafio inválido')
    else:
        print('nivel do challenge: ', res.result)
    return res.result

def getTransactionStatus(client, transaction_id=None):
    if transaction_id is None:
        transaction_id = int(input('Digite o id da transação desejada: '))
    res = client.getTransactionStatus(mine_grpc_pb2.transactionId(transactionId=transaction_id))
    print('transaction status: ', StatusEnum[res.result])
    return res.result

def getWinner(client, transaction_id=None):
    print_msgs = 1 if transaction_id is None else 0

    if transaction_id is None:
        transaction_id = int(input('Digite o id da transação desejada: '))
    res = client.getWinner(mine_grpc_pb2.transactionId(transactionId=transaction_id))

    if print_msgs:
        if res.result == -1:
            print('Desafio inválido')
        elif res.result == 0:
            print('Ainda não há ganhador')
        else:
            print('Id do ganhador: ', res.result)
    return res.result

def getSolution(client, transaction_id=None):
    if transaction_id is None:
        transaction_id = int(input('Digite o id da transação desejada: '))
    res = client.getSolution(mine_grpc_pb2.transactionId(transactionId=transaction_id))
    
    print('Status da transação: ', StatusEnum[res.status])
    print('Solução: ', res.solution)
    print('Nivel do desafio: ', res.challenge)

def validateSolution(solution, challenge):
    challenge_search = '0' * challenge
    result = bin(int(hashlib.sha1(str(solution).encode()).hexdigest(), 16))[2:].zfill(160)

    if result[:challenge] == challenge_search:
        return True
    else:
        return False

def searchSolutionThread(client, transaction_id, challenge):
    attempts = set()
    while True:
        count = 0
        while count < 5:
            random_num = random.randint(0, 10000000)

            if random_num not in attempts:
                attempts.add(random_num)
                valid = validateSolution(random_num, challenge)
                count += 1
                
                if valid:
                    
                    results = {
                        'transactionId': transaction_id,
                        'clientId': CLIENT_ID,
                        'solution': str(random_num)
                    }

                    print('Solução local encontrada: ', random_num)
                    client.submitChallenge(mine_grpc_pb2.challengeArgs(**results))

                    return
              
        if getWinner(client, transaction_id):
            print('Ganharam a transação, interrompendo mineração')
            break

def searchSolution(client, transaction_id, challenge):
    threads = []
    for _ in range(6): 
        threads.append(threading.Thread(target=searchSolutionThread, args=(client, transaction_id, challenge)))

    # Start searching solutions
    for t in threads:
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
    
def mine(client):
    """
        1. Buscar transactionID atual; -> getTransactionId()
        2. Buscar a challenge (desafio) associada à transactionID atual; -> getChallenge()
        3. Buscar, localmente, uma solução para o desafio proposto – sugere- 
        se usar múltiplas threads para isso!!!!!! -> funcao local que fica gerando strings aleatorias
        4. Imprimir localmente a solução encontrada; -> print
        5. Submeter a solução ao servidor e aguardar resultado; -> submitChallenge()
        6. Imprimir/Decodificar resposta do servidor. -> getSolution()
    """
    transaction_id = getTransactionId(client)

    if transaction_id == -1:
        print("Transação inválida, interrompendo mineração")
        return
    
    challenge = getChallenge(client, transaction_id)
    searchSolution(client, transaction_id, challenge)
    getSolution(client, transaction_id)


@breaker
def run(client, item):
    if item == 1:
        getTransactionId(client)
    elif item == 2:
        getChallenge(client)
    elif item == 3:
        getTransactionStatus(client)
    elif item == 4:
        getWinner(client)
    elif item == 5:
        getSolution(client)
    elif item == 6:
        mine(client)
       
    else:
        print('Entrada Inválida,')
    print()

@breaker
def connect():
    channel = grpc.insecure_channel('localhost:8080')
    client = mine_grpc_pb2_grpc.apiStub(channel)

    while True:
        print("*"*10)
        print('Escolha:')
        print('1 - getTransactionID,')
        print('2 - getChallenge,')
        print('3 - getTransactionStatus,')
        print('4 - getWinner,')
        print('5 - getSolution,')
        print('6 - Mine,')
        print()
        
        n = int(input('Enter your choice: '))
        
        try:
            running = run(client, n)
            # print(running)
        except pybreaker.CircuitBreakerError:
            print(pybreaker.CircuitBreakerError)

if __name__ == '__main__':
    connect()


