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
    grpc_server.wait_for_termination()

register = []

def newTransaction():
    register.append(
        {
            "transactionID": len(register),
            "challenge": random.randint(1, 6),
            "solution": None,
            "winner": -1
        }
    )

class MineServicer(mine_grpc_pb2_grpc.apiServicer):
    # TODO: ver se para a função
    def isTransactionValid(self, request, context):
        if request.transactionId < 0 or request.transactionId >= len(register):
            return mine_grpc_pb2.intResult(result=-1)

    def existsNoWinner(self, request):
        return 1 if register[request.transactionId]["winner"] == -1 else 0

    def getTransactionID(self, request, context):
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
        self.isTransactionValid(request, context)
        return mine_grpc_pb2.intResult(result=register[request.transactionId]["challenge"])
    
    def getTransactionStatus(self, request, context):
        """
        Se transactionID for válido, retorne 0 se o
        desafio associado a essa transação já foi
        resolvido. Retorne 1 caso a transação ainda
        possua desafio pendente. Retorne -1 se a
        transactionID for inválida.
        """
        self.isTransactionValid(request, context)
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

        self.isTransactionValid(request, context)

        if not self.existsNoWinner(request):
            return mine_grpc_pb2.intResult(result=2)
        
        id = request.transactionId
        challenge = register[id]["challenge"]
        challenge_search = '0' * challenge
        result = bin(int(hashlib.sha1(str(request.solution).encode()).hexdigest(), 16))[2:].zfill(160)
        
        if result[:challenge] == challenge_search: 
            register[id]["solution"] = request.solution
            register[id]["winner"] = request.clientId

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

        self.isTransactionValid(request, context)
        
        if self.existsNoWinner(request):
            return mine_grpc_pb2.intResult(result=(register[request.transactionId]["winner"]))
        else:
            return mine_grpc_pb2.intResult(result=0)
        
    
    def getSolution(self, request, context):
        """
        Retorna uma estrutura de dados (ou uma
        tupla) com o status, a solução e o desafio
        associado à transactionID.
        """
        self.isTransactionValid(request, context)

        return mine_grpc_pb2.strucResult(status=self.existsNoWinner(request), 
                                         solution=register[request.transactionId]["solution"], 
                                         challenge=register[request.transactionId]["challenge"])