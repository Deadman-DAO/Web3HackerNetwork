import json

import sys
from websocket import create_connection


class ClientInfo:
    def __init__(self, name, version):
        self.name = name
        self.version = version


class Initialize:
    def __init__(self):
        self.process_id = 666
        self.client_info = ClientInfo('wstest', '0.0.1')


print("Starting")
ws = create_connection("ws://localhost:6960/")
print("Sending stuff")
ws.send(json.dumps(Initialize()))
print("Done sending")
print(ws.recv())
ws.close()
sys.exit(-1)