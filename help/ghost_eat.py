import pygame as pg
import os
import random
import sys

pg.init()

size = height, width = 1000, 600
ghost = pg.transform.scale(pg.image.load(os.path.join('assets', 'ghostboy.png')), (50, 50))
ghost_rect = ghost.get_rect()
food = []

pg.display.set_caption('lol')
screen = pg.display.set_mode(size)
ghost_rect.y = screen.get_height() - ghost_rect.height - 5


def snow(screen):
    circlex, circley = (random.randint(10, screen.get_width()), 10)
    pg.draw.circle(screen, (0, 0, 255), (circlex, circley), 10)
    while circley < screen.get_height():
        circley += 2
        pg.draw.circle(screen, (0, 0, 255), (circlex, circley), 10)


def move(key, ghost, screen, speed):
    if key[pg.K_RIGHT] and ghost.x + ghost.width < screen.get_width():
        ghost.x += speed
    if key[pg.K_LEFT] and ghost.x > 0:
        ghost.x -= speed
    if key[pg.K_UP] and ghost.y > 0:
        ghost.y -= speed
    if key[pg.K_DOWN] and ghost.y + ghost.height < screen.get_height():
        ghost.y += speed


while True:
    for evente in pg.event.get():
        if evente.type == pg.QUIT:
            pg.quit()
            sys.exit()
    KEY_PRESSED = pg.key.get_pressed()
    screen.fill((0, 0, 0))
    move(KEY_PRESSED, ghost_rect, screen, 2)
    snow(screen)
    screen.blit(ghost, ghost_rect)

    pg.display.flip()