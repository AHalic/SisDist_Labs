import grpc
import time
import random
import hashlib
from concurrent import futures
import mine_grpc_pb2
import mine_grpc_pb2_grpc

def server():
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    mine_grpc_pb2_grpc.add_apiServicer_to_server(MineServicer(), grpc_server)
    grpc_server.add_insecure_port('[::]:8080')
    grpc_server.start()
    newTransaction()
    grpc_server.wait_for_termination()

register = []

def newTransaction():
    difficulty = random.randint(1, 6)
    print(f"New challenge: lvl {difficulty}")
    
    register.append(
        {
            "transactionID": len(register),
            "challenge": difficulty,
            "solution": None,
            "winner": 0
        }
    )

class MineServicer(mine_grpc_pb2_grpc.apiServicer):
    def isTransactionValid(self, request, context):
        if request.transactionId < 0 or request.transactionId >= len(register):
            return 1
        else:
            return 0

    def existsNoWinner(self, request):
        return 1 if register[request.transactionId]["winner"] == 0 else 0

    def getTransactionId(self, request, context):
        """
        Retorna o valor atual <int> da transação com desafio ainda pendente de solução.
        """
        return mine_grpc_pb2.intResult(result=register[-1]["transactionID"])
    
    def getChallenge(self, request, context):
        """
        Se transactionID for válido, retorne o valor
        do desafio associado a ele. Retorne -1 se o
        transactionID for inválido.
        """
        if self.isTransactionValid(request, context):
            return mine_grpc_pb2.intResult(result=-1)
        
        return mine_grpc_pb2.intResult(result=register[request.transactionId]["challenge"])
    
    def getTransactionStatus(self, request, context):
        """
        Se transactionID for válido, retorne 0 se o
        desafio associado a essa transação já foi
        resolvido. Retorne 1 caso a transação ainda
        possua desafio pendente. Retorne -1 se a
        transactionID for inválida.
        """
        if self.isTransactionValid(request, context):
            return mine_grpc_pb2.intResult(result=-1)
        return mine_grpc_pb2.intResult(result=(self.existsNoWinner(request)))

    def submitChallenge(self, request, context):
        """
        Submete uma solução (solution) para a
        função de hashing SHA-1 que resolve o
        desafio proposto para a referida
        transactionID. Retorne 1 se a solução for
        válida, 0 se for inválida, 2 se o desafio já foi
        solucionado, e -1 se a transactionID for
        inválida.
        """

        if self.isTransactionValid(request, context):
            return mine_grpc_pb2.intResult(result=-1)

        if not self.existsNoWinner(request):
            return mine_grpc_pb2.intResult(result=2)
        
        id = request.transactionId
        challenge = register[id]["challenge"]
        challenge_search = '0' * challenge
        result = bin(int(hashlib.sha1(str(request.solution).encode()).hexdigest(), 16))[2:].zfill(160)
        
        if result[:challenge] == challenge_search: 
            register[id]["solution"] = request.solution
            register[id]["winner"] = request.clientId

            newTransaction()
            return mine_grpc_pb2.intResult(result=1)
        else:
            return mine_grpc_pb2.intResult(result=0)
    
    def getWinner(self, request, context):
        """
        Retorna o clientID do vencedor da transação
        transactionID. Retorne 0 se transactionID
        ainda não tem vencedor e -1 se transactionID
        for inválida.
        """

        if self.isTransactionValid(request, context):
            return mine_grpc_pb2.intResult(result=-1)
        
        if not self.existsNoWinner(request):
            return mine_grpc_pb2.intResult(result=(register[request.transactionId]["winner"]))
        else:
            return mine_grpc_pb2.intResult(result=0)
        
    
    def getSolution(self, request, context):
        """
        Retorna uma estrutura de dados (ou uma
        tupla) com o status, a solução e o desafio
        associado à transactionID.
        """
        if self.isTransactionValid(request, context):
            return mine_grpc_pb2.intResult(result=-1)

        return mine_grpc_pb2.structResult(status=self.existsNoWinner(request), 
                                         solution=register[request.transactionId]["solution"], 
                                         challenge=register[request.transactionId]["challenge"])
    
if __name__ == '__main__':
    print("Starting server. Listening on port 8080.")
    server()