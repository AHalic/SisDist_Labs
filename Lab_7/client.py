import paho.mqtt.client as mqtt
import threading
import argparse
import hashlib
import random
import time
import uuid
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64


TIMEOUT_LIMIT = 60
# TODO!
QTDE_CLIENTS = 2
MIN_LVL = 10
MAX_LVL = 20

def parse_args() -> tuple[int, int]:
    """
    Parse command line arguments.

    Returns:
        tuple[int, int]: port, host
    """
    parser = argparse.ArgumentParser(description='Mine blocks serverless')
    parser.add_argument('--port', type=int, help='Port to listen to', default=1883)
    parser.add_argument('--host', type=str, help='Host to listen to', default='localhost')
    args = parser.parse_args()    

    return args.port, args.host

class Client:
    """
    Client class.

    Attributes:
        node_id (str): Client's UUID.
        port (int): Port to connect to.
        host (str): Host to connect to.
        public_key (str): RSA Public key in Hex.
        known_clients (list[str]): List of known clients.
        known_pub_keys (dict(NodeID: PubKey)): Dictionary of known clients NodeID as key and PubKey as value
        signer (PKCS115_SigScheme): Instance of signer from pycryptodome 
        client (mqtt.Client): MQTT client.
    """
    node_id = str(uuid.uuid4()) # TODO must be int32 in hex
    votes = []

    def __init__(self, port, host):
        """
        Constructor.

        Args:
            port (int): Port to connect to.
            host (str): Host to connect to.
        """
        print('NodeId: ', self.node_id)
        self.port = port
        self.host = host
        
        key_pair = RSA.generate(1024)
        self.public_key = key_pair.public_key().export_key().hex()


        self.known_clients = [self.node_id]
        self.known_pub_keys = dict()

        self.known_pub_keys[self.node_id] = self.public_key

        print("KNOWN PUB KEYS")
        print(self.known_pub_keys)
        print("")
        print("")
        print("")

        self.signer = PKCS1_v1_5.new(key_pair)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(host, port, 60)

        self.client.loop_forever()


    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when a connection is established with the MQTT broker.

        Args:
            client (mqtt.Client): MQTT client.
            userdata (Any): User data.
            flags (dict): Flags.
        """
        print("Connected with result code "+str(rc))

        # Topicos:
        # sd/init: NodeId <int>
        # sd/voting: NodeId <int>, Vote <int>
        # sd/result: NodeId <int>, TransactionID <int>, Solution <string>, Result <int>
        # sd/challenge: TransactionID <int>, Challenge <string>
        client.subscribe([("sd/init", 0), ("sd/pubkey", 0), ("sd/voting", 0), ("sd/result", 0), ("sd/challenge", 0)])
        threading.Thread(target=self.send_init).start()

    def send_init(self):
        """
        Send init message until all clients are known or timeout.
        """
        start = time.time()
        msg = json.dumps({"NodeId": self.node_id})

        while time.time() - start < TIMEOUT_LIMIT or len(self.known_clients) < QTDE_CLIENTS:
            self.client.publish("sd/init", msg)
            time.sleep(5)

    def sign_and_send(self, topic, msg_json):
        hash = SHA256.new()
        hash.update(str.encode(msg_json))
        sign = self.signer.sign(hash)
        
        sign_str = base64.b64encode(sign).decode()
        
        msg = json.dumps({"Payload": msg_json, "Sign": sign_str, "NodeId": self.node_id})
        self.client.publish(topic, msg)


    def on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the MQTT broker.
        Depending on the topic of the message calls the appropriate function.

        Args:
            client (mqtt.Client): MQTT client.
            userdata (Any): User data.
            msg (mqtt.MQTTMessage): Message.
        """
        msg = json.loads(msg.payload)
        payload = msg["Payload"]

        if msg.topic == "sd/init":
            self.on_init(payload)
        
        elif msg.topic == "sd/pubkey":
            self.on_pubkey(payload)

        else:
            client = msg["NodeId"]
            sign = msg["Sign"]

            msg_hash = SHA256.new()
            msg_hash.update(str.encode(payload))

            pub_key = RSA.import_key(bytes.fromhex(self.known_pub_keys[client]))
            print("trying: ", pub_key)
            verified = PKCS1_v1_5.new(pub_key).verify(msg_hash, sign)

            if not verified:
                raise "Message sign verification failed"
            elif msg.topic == "sd/voting":
                self.on_voting(payload)

            elif msg.topic == "sd/result":
                self.on_result(payload)

            elif msg.topic == "sd/challenge":
                self.on_challenge(payload)

            elif msg.topic == "sd/solution":
                self.on_solution(payload)

    def on_pubkey(self, msg):
        """
        Function for when a public_key message is received from the MQTT broker.
        The key and node_id is added as a dictionary to the list of known_pub_keys
        
        Args:
            msg (mqtt.MQTTMessage): Message.
        """
        msg_json =  json.loads(msg)
        client_id = msg_json['NodeId']
        client_public_key = msg_json['PubKey']

        self.known_pub_keys[client_id] = client_public_key

        if len(self.known_pub_keys) == len(self.known_clients):
            self.client.unsubscribe('sd/pubkey')

            self.send_voting()

    def on_init(self, msg):
        """
        Function for when a init message is received from the MQTT broker.
        If the client is not known and the number of known clients is less than the number of clients needed,
        the client is added to the list of known clients.
        If the number of known clients is equal to the number of clients needed, the client unsubscribes from the init topic
        and starts the voting.

        Args:
            msg (mqtt.MQTTMessage): Message.
        """
        client_id = json.loads(msg)['NodeId']
        print('mensagem de init', msg)

        if client_id not in self.known_clients and len(self.known_clients) < QTDE_CLIENTS:
            self.known_clients.append(client_id)
        if len(self.known_clients) == QTDE_CLIENTS:
            self.client.unsubscribe("sd/init")
            print('iniciando troca de chaves publicas')

            self.send_pubkey()

    def send_pubkey(self):
        """
        Function for when all nodes are known. Nodes start to exchange public_keys
        """
        msg = json.dumps({"NodeId": self.node_id, "PubKey": self.public_key})
        
        while len(self.known_pub_keys) < len(self.known_clients):
            self.client.publish("sd/pubkey", msg)
            time.sleep(5)

    def on_voting(self, msg):
        """
        Function for when a voting message is received from the MQTT broker.
        If the number of votes is equal to the number of clients needed, the client unsubscribes from the voting topic
        and elect the controller.

        Args:
            msg (mqtt.MQTTMessage): Message.
        """
        msg_json = json.loads(msg)
        print('mensagem de voto', msg)
        
        if msg_json['NodeId'] not in self.votes:
            self.votes.append(msg_json)

        if len(self.votes) == QTDE_CLIENTS:
            self.client.unsubscribe("sd/voting")
            print('Votação encerrada')
            
            self.elect_leader()

    def on_result(self, msg):
        """
        Function for when a result message is received from the MQTT broker.

        Args:
            msg (mqtt.MQTTMessage): Message.
        """
        msg_json = json.loads(msg)

        if msg_json['Result'] == 1 and msg_json['TransactionID'] == self.challenge['TransactionID']:
            print('\nSolução encontrada: ', msg_json['Solution'])
            print('Ganhador: ', msg_json['NodeId'])
            self.solution_found = True

    def on_challenge(self, msg):
        """
        Function for when a challenge message is received from the MQTT broker.
        """
        msg_json = json.loads(msg)
        self.challenge = msg_json
        self.solution_found = False

        print('\nNovo desafio recebido, dificuldade: ', msg_json['Challenge'])
        self.search_solution()

    def on_solution(self, msg):
        """
        Function for when a solution message is received from the MQTT broker.
        The controller validates the solution and sends a message to the broker saying if it is valid or not.

        Args:
            msg (mqtt.MQTTMessage): Message.
        """
        msg_json = json.loads(msg)

        challenge = self.challenges[msg_json['TransactionID']]

        result = {
            'NodeId': msg_json['NodeId'],
            'TransactionID': msg_json['TransactionID'],
            'Solution': msg_json['Solution'],
        }

        if self.validate_solution(msg_json['Solution'], challenge['Challenge']) and challenge['Winner'] == 0:
            result['Result'] = 1
            challenge['Winner'] = msg_json['NodeId']
            challenge['Solution'] = msg_json['Solution']

            print('\nSolução encontrada: ', msg_json['Solution'])
            print('Ganhador: ', msg_json['NodeId'])
        else:
            result['Result'] = 0

        self.sign_and_send("sd/result", json.dumps(result))

        if result['Result'] == 1:
            threading.Thread(target=self.show_menu).start()

    def validate_solution(self, solution, challenge):
        """
        Function to validate the solution of the challenge.

        Args:
            solution (int): Solution of the challenge.
            challenge (int): Challenge difficulty.

        Returns:
            bool: True if the solution is valid, False otherwise.
        """
        challenge_search = '0' * challenge
        result = bin(int(hashlib.sha1(str(solution).encode()).hexdigest(), 16))[2:].zfill(160)

        if result[:challenge] == challenge_search:
            return True
        else:
            return False

    def search_solution_thread(self, transaction_id, challenge):
        """
        Function to search for a solution to the challenge.
        
        Args:
            transaction_id (int): Transaction ID.
            challenge (int): Challenge difficulty.
        """
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
                            'NodeId': self.node_id,
                            'Solution': str(random_num)
                        }

                        print('Solução local encontrada: ', random_num)
                        if not self.solution_found:
                            msg = json.dumps(result)
                            digest.update(msg.encode("utf-8"))
                            self.sign_and_send("sd/solution",)

                        return
                
            if self.solution_found:
                print('Ganharam a transação, interrompendo mineração')
                break

    def search_solution(self):
        """
        Function that creates Threads to search for a solution to the challenge.
        """
        threads = []
        for _ in range(6): 
            threads.append(threading.Thread(target=self.search_solution_thread, args=(self.challenge['TransactionID'], self.challenge['Challenge'])))

        # Start searching solutions
        for t in threads:
            t.start()


    def send_voting(self):
        """
        Function to send a voting message to the MQTT broker.
        """
        vote = uuid.uuid4()
        vote_msg = json.dumps({"NodeId": self.node_id, "VoteID": str(vote)})

        self.sign_and_send("sd/voting", vote_msg)    

    def elect_leader(self):
        """
        Function to elect the controller.
        If the client is the controller, it unsubscribes from the voting topic, subscribes to the challenge topic
        and shows the menu.
        """

        # finds vote of biggest value, if there is a tie, client ID is used as tie breaker
        max_vote = max(self.votes, key=lambda x: (x['VoteID'], x['NodeId']))

        if max_vote['NodeId'] == self.node_id:
            self.client.unsubscribe(["sd/result", "sd/challenge"])
            
            self.client.subscribe("sd/solution")
            self.challenges = []

            self.show_menu()
         
    def show_menu(self):
        """
        Function to show the controller's menu.
        """
        print("\nEscolha uma das opções abaixo:")
        print("1 - Iniciar desafio")
        print("2 - Encerrar")

        option = int(input("Opção: "))
        if option == 1:
            self.new_transaction()
        elif option == 2:
            self.client.disconnect()

    def new_transaction(self):
        """
        Function to create a new transaction.
        """
        difficulty = random.randint(MIN_LVL, MAX_LVL)
        print(f"New challenge: lvl {difficulty}")
        
        challenge = {
            "TransactionID": len(self.challenges),
            "Challenge": difficulty,
            "Solution": None,
            "Winner": 0
        }
        self.challenges.append(challenge)

        self.sign_and_send("sd/challenge", json.dumps({"TransactionID": challenge["TransactionID"], "Challenge": challenge["Challenge"]}))


if __name__ == "__main__":
    port, host = parse_args()
    client = Client(port, host)