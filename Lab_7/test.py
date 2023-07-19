import paho.mqtt.client as mqtt
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64

if __name__ == "__main__":
    key_pair_1 = RSA.generate(1024)
    private_key_1 = key_pair_1.export_key().hex()
    public_key_1 = key_pair_1.public_key().export_key().hex()

    signer_1 = PKCS1_v1_5.new(key_pair_1)

    payload = json.dumps({"ClientID": 1})

    hash = SHA256.new()
    hash.update(str.encode(payload))

    sign = signer_1.sign(hash)

    sign_str = base64.b64encode(sign).decode()

    print(sign)
    msg_1 = json.dumps({"Payload": payload, "Sign": sign_str})

    msg_load = json.loads(msg_1)

    loaded_content = msg_load["Payload"]
    
    sign = msg_load["Sign"]

    msg_hash = SHA256.new()
    msg_hash.update(str.encode(loaded_content))

    verifier = PKCS1_v1_5.new(RSA.import_key(bytes.fromhex(public_key_1)))
    verified = verifier.verify(msg_hash, base64.b64decode(sign))

    real = json.loads(loaded_content)
    print (real["ClientID"])

    if verified:
        print("SUCCESS")
    else:
        print("FAIL")