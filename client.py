import socket
import json

class Client():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.__counter = 0
        self.peer_data = None

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            while True:
                try:
                    request = s.recv(1024)
                    if not request:
                        print("[Client] Server disconnected.")
                        break
                    decoded = json.loads(request.decode('utf-8'))
                    print(f"[Client] Server says: {decoded}")
                    self.peer_data = decoded

                    action = decoded.get("action")
                    if action == "get_counter":
                        data = {"counter": self.__counter}
                        s.sendall(json.dumps(data).encode('utf-8'))
                except Exception as e:
                    print(f"[Client] Error: {e}")
                    break

    def update_counter(self, counter):
        self.__counter = counter