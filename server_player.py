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
        
    def __setup__(self):
        host, port = self.host, self.port
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, port))
        lsock.listen()
        print(f"Listening on {(host, port)}")
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        message = server_message.Message(self.sel, conn, addr, "hello world from server")
        self.sel.register(conn, selectors.EVENT_READ, data=message)

    def check_server_socket(self):
        if not self.is_socket_locked:
            self.is_socket_locked = True
            try:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
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