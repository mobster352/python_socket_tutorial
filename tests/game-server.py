import selectors
import socket
import sys
import traceback

import server_message

import time

sel = selectors.DefaultSelector()

num_connections = 0
client_1_port = None
client_2_port = None
client_1_conn = None
client_2_conn = None

client_1_counter = 0
client_2_counter = 0

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    global num_connections
    global client_1_port
    global client_2_port
    global client_1_conn
    global client_2_conn
    if num_connections == 0:
        num_connections += 1
        client_1_port = addr[1]
        client_1_conn = conn
    else:
        num_connections += 1
        client_2_port = addr[1]
        client_2_conn = conn
    conn.setblocking(False)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = server_message.Message(sel, conn, addr)
    sel.register(conn, events, data=message)

    # print(f"Num conns: {num_connections}")
    # print(f"Client 1 Port: {client_1_port}")
    # print(f"Client 2 Port: {client_2_port}")

def main():
    host, port = '127.0.0.1', 65432

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen(2)
    print(f"Listening on {(host, port)}")
    lsock.setblocking(False)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(lsock, events, data=None)   

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    message = key.data
                    try:
                        if mask & selectors.EVENT_READ:
                            if message.addr[1] == client_1_port:
                                global client_1_counter
                                client_1_counter = message.process_events(mask, client_1_counter)
                                if client_1_counter is not None:
                                    client_1_counter = client_1_counter["counter"]["value"]
                            else:
                                global client_2_counter
                                client_2_counter = message.process_events(mask, client_1_counter)
                            print(f"Client 1 counter: {client_1_counter}")
                            # print(f"Client 1 counter: {client_1_counter}")
                            # print(f"Message.addr: {message.addr[1]}")
                            # print(f"Client 1 port: {client_1_port}")
                            # print(f"Client 2 port: {client_2_port}")
                        if mask & selectors.EVENT_WRITE:
                            message.process_events(mask, client_1_counter)
                            # time.sleep(5)
                    except BufferError as e:
                        print(e)
                        time.sleep(5)
                        message.get_data("get_counter")
                    except RuntimeError as e:
                        print(e)
                    except Exception:
                        print(
                            f"Main: Error: Exception for {message.addr}:\n"
                            f"{traceback.format_exc()}"
                        )
                        message.close()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()


if __name__ == "__main__":
    main()