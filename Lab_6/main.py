import paho.mqtt.client as mqtt
from decouple import config
import logging
import random

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Client:
    voting_queue = config('VOTING_QUEUE', default='sd/voting')
    result_queue = config('RESULT_QUEUE', default='sd/result')
    solution_queue = config('SOLUTION_QUEUE', default='sd/solution')
    challenge_queue = config('CHALLENGE_QUEUE', default='sd/challenge')
    total_clients = []

    init_voting = False

    def __init__(self):
        self.client_id = random.randint(1, 1000)
        
        self.init_client = mqtt.Client()
        self.voting_client = mqtt.Client()
        self.result_client = mqtt.Client()
        self.solution_client = mqtt.Client()
        self.challenge_client = mqtt.Client()

        self.configure_init_client()
        

    def configure_init_client(self):
        def init_connect(client, userdata, flags, rc):
            logger.info("Connected with result code "+str(rc))

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe(config('INIT_QUEUE', default='sd/init'))
            self.total_clients.append(self.client_id)

        
        def init_message(client, userdata, msg):
            logger.info(f"New player connected: {int((msg.payload))}")
            
            if len(self.total_clients) < 10:
                logger.info(f"Total players: {len(self.total_clients)}")
                self.total_clients.append(int(msg.payload))

            if len(self.total_clients) == 10 and not self.init_voting:
                logger.info("Starting voting")
                self.init_client.publish(config('VOTING_QUEUE', default='sd/voting'), "start")    
                self.init_voting = True

        self.init_client.on_connect = init_connect
        self.init_client.on_message = init_message
        self.init_client.connect("localhost", 1883, 60)
        self.init_client.publish(config('INIT_QUEUE', default='sd/init'), self.client_id)
        self.init_client.loop_forever()

if __name__ == '__main__':
    client = Client()