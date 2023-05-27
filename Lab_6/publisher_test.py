import paho.mqtt.publish as publish
import argparse

def parse_args() -> tuple[int, int]:
    parser = argparse.ArgumentParser(description='Mine blocks serverless')
    parser.add_argument('--port', type=int, help='Port to listen to', default=1883)
    parser.add_argument('--host', type=str, help='Host to listen to', default='localhost')
    args = parser.parse_args()    

    return args.port, args.host


if __name__ == "__main__":
    port, host = parse_args()

    publish.single("sd/init", "payload", hostname=host, port=port)
    publish.single("sd/result", "resultado", hostname=host, port=port)