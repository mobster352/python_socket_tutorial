import socket
import threading
import time
import json

HOST = '127.0.0.1'
PORT = 65432
MAX_CONNECTIONS = 2

# Shared state
clients = [None, None]  # (conn, addr)
counters = [0, 0]
lock = threading.Lock()

def handle_client(conn, addr, index):
    global clients, counters
    print(f"[+] Client {index+1} connected: {addr}")
    try:
        while True:
            with lock:
                other_index = 1 - index
                counter_value = counters[other_index]
                request = {"action": "get_counter", "counter": counter_value}
            
            # Send request
            try:
                conn.sendall(json.dumps(request).encode('utf-8'))
            except (BrokenPipeError, ConnectionResetError) as e:
                print(f"[!] Client {index+1} send error: {e}")
                break

            # Receive response
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"[-] Client {index+1} disconnected")
                    break
                value = int.from_bytes(data, byteorder='big')
                with lock:
                    counters[index] = value
                    print(f"[#] Client {index+1} Counter: {value}")
            except Exception as e:
                print(f"[!] Error receiving from Client {index+1}: {e}")
                break

            time.sleep(0.1)  # Reduce CPU usage
    finally:
        with lock:
            clients[index] = None
            counters[index] = 0
            print(f"[x] Client {index+1} cleanup done.")
        conn.close()

def find_free_slot():
    with lock:
        for i in range(MAX_CONNECTIONS):
            if clients[i] is None:
                return i
    return None

# Main server loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT}...")

    while True:
        conn, addr = s.accept()
        slot = find_free_slot()
        if slot is None:
            print("[!] Connection refused: max clients reached")
            conn.close()
            continue
        with lock:
            clients[slot] = (conn, addr)
        thread = threading.Thread(target=handle_client, args=(conn, addr, slot), daemon=True)
        thread.start()
