import socket
import json

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    counter = 0
    while True:
        try:
            request = s.recv(1024)
            if not request:
                print("[Client] Server disconnected.")
                break
            decoded = json.loads(request.decode('utf-8'))
            print(f"[Client] Server says: {decoded}")

            action = decoded.get("action")
            if action == "get_counter":
                counter += 1
                s.sendall(counter.to_bytes(4, byteorder='big'))
        except Exception as e:
            print(f"[Client] Error: {e}")
            break
