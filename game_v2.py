import pygame
import pygame.freetype

from button import Button
from client import Client

import threading

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    dt = 0
    fps = 60

    host, port = '127.0.0.1', 65432

    font = pygame.freetype.Font(None, 30)

    run = True

    counter = 0

    client_connect_button = Button("Client Connect", 1280, 720, 2, 2)

    client = None

    while run:
        event_list = pygame.event.get()

        for event in event_list:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if client_connect_button.check_collisions(mouse_pos):
                    client = Client(host, port)
                    client_thread = threading.Thread(target=client.connect)
                    client_thread.daemon = True
                    client_thread.start()

        screen.fill("black")

        if client == None:
            client_connect_button.update_button(1280, 720)
            client_connect_button.draw_button("white", "red", font, screen)
        elif client != None:
            client.update_counter(counter)

            counter_surface, rect = font.render(f"Client Counter: {counter}", "white", (0,0,0))
            screen.blit(counter_surface, (20, 10))

            if client.peer_data is None:
                counter_surface, rect = font.render(f"Peer Counter: 0", "white", (0,0,0))
            else:
                counter_surface, rect = font.render(f"Peer Counter: {client.peer_data["counter"]}", "white", (0,0,0))
            screen.blit(counter_surface, (400, 10))

        pygame.display.flip()

        dt = clock.tick(fps) / 1000

        counter += 1

if __name__ == "__main__":
    main()