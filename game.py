import pygame
import pygame.freetype

from button import Button
from server_player import Server_Player
from client_player import Client_Player

import threading

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    dt = 0
    fps = 60

    font = pygame.freetype.Font(None, 30)

    run = True

    counter = 0

    server_connect_button = Button("Server Connect", 1280, 720, 2, 2.5)

    client_connect_button = Button("Client Connect", 1280, 720, 2, 2)

    host, port = '127.0.0.1', 65432
    server_player = None
    client_player = None

    while run:
        event_list = pygame.event.get()

        for event in event_list:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if server_connect_button.check_collisions(mouse_pos):
                    server_player = Server_Player(host, port)
                if client_connect_button.check_collisions(mouse_pos):
                    client_player = Client_Player(host, port, counter)

        screen.fill("black")

        if server_player == None and client_player == None:
            server_connect_button.update_button(1280, 720)
            server_connect_button.draw_button("white", "blue", font, screen)

            client_connect_button.update_button(1280, 720)
            client_connect_button.draw_button("white", "red", font, screen)
        elif server_player != None:
            counter_surface, rect = font.render(f"Server Counter: {counter}", "white", (0,0,0))
            screen.blit(counter_surface, (20, 10))

            server_thread = threading.Thread(target=server_player.check_server_socket, args=(counter,))
            server_thread.daemon = True
            server_thread.start()

            counter_surface, rect = font.render(f"Client Counter: {server_player.peer_data}", "white", (0,0,0))
            screen.blit(counter_surface, (400, 10))
        elif client_player != None:
            # client_player.setup_request(counter)

            counter_surface, rect = font.render(f"Client Counter: {counter}", "white", (0,0,0))
            screen.blit(counter_surface, (20, 10))

            client_thread = threading.Thread(target=client_player.check_client_socket)
            client_thread.daemon = True
            client_thread.start()

            if client_player.peer_data is None:
                counter_surface, rect = font.render(f"Server Counter None: {client_player.peer_data}", "white", (0,0,0))
            else:
                counter_surface, rect = font.render(f"Server Counter: {client_player.peer_data["counter"]["value"]}", "white", (0,0,0))
            screen.blit(counter_surface, (400, 10))

        pygame.display.flip()

        dt = clock.tick(fps) / 1000

        counter += 1

if __name__ == "__main__":
    main()