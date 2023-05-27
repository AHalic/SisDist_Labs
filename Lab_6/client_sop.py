import paho.mqtt.client as mqtt
import threading
import argparse
import random
import time
import uuid
import json

TIMEOUT_LIMIT = 60
QTDE_CLIENTS = 2

def parse_args() -> tuple[int, int]:
    parser = argparse.ArgumentParser(description='Mine blocks serverless')
    parser.add_argument('--port', type=int, help='Port to listen to', default=1883)
    parser.add_argument('--host', type=str, help='Host to listen to', default='localhost')
    args = parser.parse_args()    

    return args.port, args.host

class Client:
    uuid = str(uuid.uuid4())
    votes = []

    def __init__(self, port, host):
        self.port = port
        self.host = host
        self.known_clients = [self.uuid]

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(host, port, 60)

        self.client.loop_forever()


    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Topicos:
        # sd/init: ClientID <int>
        # sd/voting: ClientID <int>, Vote <int>
        # sd/result: ClientID <int>, TransactionID <int>, Solution <string>, Result <int>
        # sd/challenge: TransactionID <int>, Challenge <string>
        threading.Thread(target=self.send_init).start()
        client.subscribe([("sd/init", 0), ("sd/voting", 0), ("sd/result", 0), ("sd/challenge", 0)])

    def send_init(self):
        start = time.time()
        msg = json.dumps({"ClientID": self.uuid})

        while time.time() - start < TIMEOUT_LIMIT or len(self.known_clients) < QTDE_CLIENTS:
            self.client.publish("sd/init", msg)
            time.sleep(10)

    def on_message(self, client, userdata, msg):
        if msg.topic == "sd/init":
            self.on_init(msg.payload)

        elif msg.topic == "sd/voting":
            self.on_voting(msg.payload)

        elif msg.topic == "sd/result":
            self.on_result(msg.payload)

        elif msg.topic == "sd/challenge":
            self.on_challenge(msg.payload)


    def on_init(self, msg):
        client_id = json.loads(msg)['ClientID']

        if client_id not in self.known_clients and len(self.known_clients) < QTDE_CLIENTS:
            self.known_clients.append(client_id)
        if len(self.known_clients) == QTDE_CLIENTS:
            self.client.unsubscribe("sd/init")
            print('iniciando votação')
            self.send_voting()

        print('mensagem de init', msg)

    def on_voting(self, msg):
        msg_json = json.loads(msg)
        
        if msg_json['ClientID'] not in self.votes:
            self.votes.append(msg_json)

        if len(self.votes) == QTDE_CLIENTS:
            self.client.unsubscribe("sd/voting")
            print('Votação encerrada')
            
            self.elect_leader()

        print('mensagem de voto', msg)

    def on_result(self, msg):
        print('mensagem de resultado', msg)

    def on_challenge(self, msg):
        print('mensagem de challenge', msg)

    def send_voting(self):
        vote = uuid.uuid4()
        vote_msg = json.dumps({"ClientID": self.uuid, "VoteID": str(vote)})

        self.client.publish("sd/voting", vote_msg)    

    def elect_leader(self):
        # finds vote of biggest value, if there is a tie, client ID is used as tie breaker
        max_vote = max(self.votes, key=lambda x: (x['VoteID'], x['ClientID']))
        print()
        print(max_vote)
        print()
        if max_vote['ClientID'] == self.uuid:
            self.client.unsubscribe(["sd/result", "sd/challenge"])
            
            self.client.subscribe("sd/solution")
            self.challenges = []

            self.show_menu()
        
    
    def show_menu(self):
        print("Escolha uma das opções abaixo:")
        print("1 - Iniciar desafio")
        print("2 - Encerrar")

        option = int(input("Opção: "))
        if option == 1:
            self.newTransaction()
        elif option == 2:
            self.client.disconnect()


    def newTransaction(self):
        difficulty = random.randint(1, 6)
        print(f"New challenge: lvl {difficulty}")
        
        challenge = {
            "transactionID": len(self.challenges),
            "challenge": difficulty,
            "solution": None,
            "winner": 0
        }
        self.challenges.append(challenge)

        self.client.publish("sd/challenge", json.dumps({"TransactionID": challenge["transactionID"], "Challenge": challenge["challenge"]}))


if __name__ == "__main__":
    port, host = parse_args()
    client = Client(port, host)