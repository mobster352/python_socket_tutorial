import selectors
import socket
import sys
import traceback

import client_message

import queue

class Client_Player:
    def __init__(self, host, port, counter):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.request = self.create_request(counter)
        self.is_socket_locked = False
        self.peer_data = None

        self.addr = (self.host, self.port)
        print(f"Starting connection to {self.addr}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setblocking(False)
        self.sock.connect_ex(self.addr)
        self.events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = client_message.Message(self.sel, self.sock, self.addr, self.request)
        self.sel.register(self.sock, self.events, data=message)

    def setup_request(self, counter):
        self.request = self.create_request(counter)
        self.start_connection()

    def create_request(self, value):
        return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(value=value),
            )

    def start_connection(self):
        message = client_message.Message(self.sel, self.sock, self.addr, self.request)
        self.sel.modify(self.sock, self.events, data=message)

    def check_client_socket(self):
        if not self.is_socket_locked:
            self.is_socket_locked = True
            try:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    message = key.data
                    try:
                        if mask & selectors.EVENT_READ:
                            self.peer_data = message.process_events(mask)
                            # self.is_socket_locked = False
                        if mask & selectors.EVENT_WRITE:
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
                # pass