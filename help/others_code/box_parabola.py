import random

import pygame

pygame.init()

screen = pygame.display.set_mode((500, 500))
screen_rect = screen.get_rect()

clock = pygame.time.Clock()

G = pygame.Vector2(0, 200)  # units of pixels per second per second

box = pygame.Surface((10, 50))
box.fill("red")
box_pos = pygame.Vector2(50, screen_rect.bottom)
box_velocity = pygame.Vector2(0, 500)
rect = box.get_rect(bottomleft=box_pos)

coefficient = 1000
fps = 60
direction = 1


def do_gravity(pos, velocity, dt):
    pos += velocity * dt + 1 / 2 * G * dt**2
    velocity += G * dt
    if velocity.y > 500:
        velocity.y = 500


def main():
    global coefficient, direction

    running = True
    while running:
        dt = clock.tick(fps) / coefficient
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and rect.bottom == screen_rect.height:
                    box_velocity.y = -200
                    if direction == 1:
                        box_velocity.x = random.randint(0, (screen_rect.width - rect.centerx) // 3)
                    else:
                        box_velocity.x = random.randint(-rect.centerx // 3, 0)
                    direction *= -1

        do_gravity(box_pos, box_velocity, dt)
        rect.center = box_pos
        if rect.bottom > screen_rect.height:
            rect.bottom = screen_rect.height
            box_pos.xy = rect.center
            box_velocity.x = 0

        # screen.fill("white")
        screen.blit(box, rect)
        pygame.display.flip()


if __name__ == '__main__':
    main()