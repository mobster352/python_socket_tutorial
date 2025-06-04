import selectors
import socket
import sys
import traceback

import server_message

class Server_Player:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.__setup__()
        self.is_socket_locked = False
        self.peer_data = None
        
    def __setup__(self):
        host, port = self.host, self.port
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, port))
        lsock.listen()
        print(f"Listening on {(host, port)}")
        lsock.setblocking(False)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(lsock, events, data=None)

    def accept_wrapper(self, sock, counter):
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = server_message.Message(self.sel, conn, addr, counter)
        self.sel.register(conn, events, data=message)

    def check_server_socket(self, counter):
        if not self.is_socket_locked:
            self.is_socket_locked = True
            try:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj, counter)
                    else:
                        message = key.data
                        try:
                            if mask & selectors.EVENT_READ:
                                self.peer_data = message.process_events(mask)
                                # print(f"Peer data: {self.peer_data}")
                            if mask & selectors.EVENT_WRITE:
                                message.process_events(mask)
                                # self.is_socket_locked = False
                        except Exception:
                            print(
                                f"Main: Error: Exception for {message.addr}:\n"
                                f"{traceback.format_exc()}"
                            )
                            message.close()
            except KeyboardInterrupt:
                print("Caught keyboard interrupt, exiting")
            finally:
                # self.sel.close()
                self.is_socket_locked = False