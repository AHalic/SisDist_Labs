import paho.mqtt.publish as publish

publish.single("sd/init", "payload", hostname="localhost")