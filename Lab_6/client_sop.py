import paho.mqtt.client as mqtt
import threading
import argparse
import hashlib
import random
import time
import uuid
import json

TIMEOUT_LIMIT = 60
QTDE_CLIENTS = 3

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
        print('UUID: ', self.uuid)
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
        client.subscribe([("sd/init", 0), ("sd/voting", 0), ("sd/result", 0), ("sd/challenge", 0)])
        threading.Thread(target=self.send_init).start()

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

        elif msg.topic == "sd/solution":
            self.on_solution(msg.payload)

    def on_init(self, msg):
        client_id = json.loads(msg)['ClientID']
        print('mensagem de init', msg)

        if client_id not in self.known_clients and len(self.known_clients) < QTDE_CLIENTS:
            self.known_clients.append(client_id)
        if len(self.known_clients) == QTDE_CLIENTS:
            self.client.unsubscribe("sd/init")
            print('iniciando votação')
            self.send_voting()

    def on_voting(self, msg):
        msg_json = json.loads(msg)
        print('mensagem de voto', msg)
        
        if msg_json['ClientID'] not in self.votes:
            self.votes.append(msg_json)

        if len(self.votes) == QTDE_CLIENTS:
            self.client.unsubscribe("sd/voting")
            print('Votação encerrada')
            
            self.elect_leader()

    def on_result(self, msg):
        msg_json = json.loads(msg)

        if msg_json['Result'] == 1 and msg_json['TransactionID'] == self.challenge['TransactionID']:
            print('\nSolução encontrada: ', msg_json['Solution'])
            print('Ganhador: ', msg_json['ClientID'])
            self.solution_found = True

    def on_challenge(self, msg):
        msg_json = json.loads(msg)
        self.challenge = msg_json
        self.solution_found = False

        print('\nNovo desafio recebido, dificuldade: ', msg_json['Challenge'])
        self.search_solution()

    def on_solution(self, msg):
        msg_json = json.loads(msg)

        challenge = self.challenges[msg_json['TransactionID']]

        result = {
            'ClientID': msg_json['ClientID'],
            'TransactionID': msg_json['TransactionID'],
            'Solution': msg_json['Solution'],
        }

        if self.validate_solution(msg_json['Solution'], challenge['Challenge']) and challenge['Winner'] == 0:
            result['Result'] = 1
            challenge['Winner'] = msg_json['ClientID']
            challenge['Solution'] = msg_json['Solution']

            print('\nSolução encontrada: ', msg_json['Solution'])
            print('Ganhador: ', msg_json['ClientID'])
        else:
            result['Result'] = 0

        self.client.publish("sd/result", json.dumps(result))

        if result['Result'] == 1:
            threading.Thread(target=self.show_menu).start()

    def validate_solution(self, solution, challenge):
        challenge_search = '0' * challenge
        result = bin(int(hashlib.sha1(str(solution).encode()).hexdigest(), 16))[2:].zfill(160)

        if result[:challenge] == challenge_search:
            return True
        else:
            return False

    def search_solution_thread(self, transaction_id, challenge):
        attempts = set()
        while True:
            count = 0
            while count < 5:
                random_num = random.randint(0, 10000000)

                if random_num not in attempts:
                    attempts.add(random_num)
                    valid = self.validate_solution(random_num, challenge)
                    count += 1
                    
                    if valid:
                        
                        result = {
                            'TransactionID': transaction_id,
                            'ClientID': self.uuid,
                            'Solution': str(random_num)
                        }

                        print('Solução local encontrada: ', random_num)
                        if not self.solution_found:
                            self.client.publish("sd/solution", json.dumps(result))

                        return
                
            if self.solution_found:
                print('Ganharam a transação, interrompendo mineração')
                break

    def search_solution(self):
        threads = []
        for _ in range(6): 
            threads.append(threading.Thread(target=self.search_solution_thread, args=(self.challenge['TransactionID'], self.challenge['Challenge'])))

        # Start searching solutions
        for t in threads:
            t.start()


    def send_voting(self):
        vote = uuid.uuid4()
        vote_msg = json.dumps({"ClientID": self.uuid, "VoteID": str(vote)})

        self.client.publish("sd/voting", vote_msg)    

    def elect_leader(self):
        # finds vote of biggest value, if there is a tie, client ID is used as tie breaker
        max_vote = max(self.votes, key=lambda x: (x['VoteID'], x['ClientID']))

        if max_vote['ClientID'] == self.uuid:
            self.client.unsubscribe(["sd/result", "sd/challenge"])
            
            self.client.subscribe("sd/solution")
            self.challenges = []

            self.show_menu()
         
    def show_menu(self):
        print("\nEscolha uma das opções abaixo:")
        print("1 - Iniciar desafio")
        print("2 - Encerrar")

        option = int(input("Opção: "))
        if option == 1:
            self.newTransaction()
        elif option == 2:
            self.client.disconnect()

    def newTransaction(self):
        difficulty = random.randint(10, 20)
        print(f"New challenge: lvl {difficulty}")
        
        challenge = {
            "TransactionID": len(self.challenges),
            "Challenge": difficulty,
            "Solution": None,
            "Winner": 0
        }
        self.challenges.append(challenge)

        self.client.publish("sd/challenge", json.dumps({"TransactionID": challenge["TransactionID"], "Challenge": challenge["Challenge"]}))


if __name__ == "__main__":
    port, host = parse_args()
    client = Client(port, host)