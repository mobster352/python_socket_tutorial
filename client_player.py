import selectors
import socket
import sys
import traceback

import client_message

class Client_Player:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.request = None
        self.__setup__()
        self.is_socket_locked = False

    def __setup__(self):
        self.request = self.create_request("hello world from client")
        self.start_connection()

    def create_request(self, value):
        return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(value=value),
            )

    def start_connection(self):
        addr = (self.host, self.port)
        print(f"Starting connection to {addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = client_message.Message(self.sel, sock, addr, self.request)
        self.sel.register(sock, events, data=message)

    def check_client_socket(self):
        if not self.is_socket_locked:
            self.is_socket_locked = True
            try:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        print(
                            f"Main: Error: Exception for {message.addr}:\n"
                            f"{traceback.format_exc()}"
                        )
                        message.close()
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    return
            except KeyboardInterrupt:
                print("Caught keyboard interrupt, exiting")
            finally:
                # self.sel.close()
                self.is_socket_locked = False