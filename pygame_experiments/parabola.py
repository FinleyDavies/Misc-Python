
import pygame
from pygame import Vector2, Surface
from math import sqrt

WIDTH, HEIGHT = 600, 600
DT = 1 / 60 * 10


def get_vector(g, h1, h2, x, use_2nd_root=True):
    coefficient = -1 if use_2nd_root else 1
    vel_y = sqrt(2 * g * h1)
    # t1 = 2 * vel_y / g
    t2 = (coefficient * sqrt(2 * -g * h2 + vel_y ** 2) - vel_y) / g
    vel_x = x / t2

    return Vector2(vel_x, -vel_y)


class Particle:
    def __init__(self, screen: Surface, position: Vector2, velocity: Vector2):
        self.screen = screen
        self.position = position
        self.velocity = velocity

        self.velocity.y += 9.8 * DT / 2
        self.dead = False

    def update(self):
        if not self.dead:
            if self.position.y > HEIGHT or not 20 < self.position.x < WIDTH:
                self.dead = True
                return

            self.position += self.velocity * DT
            self.velocity.y += 9.8 * DT

            pygame.draw.circle(self.screen, (255, 255, 255), self.position, 3)






def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    particles = []

    second_root = True
    running = True
    while running:

        p1 = WIDTH // 2, HEIGHT // 2
        p2 = pygame.mouse.get_pos()
        h1 = 100

        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                second_root = not second_root or p2[1] > WIDTH // 2 - 1


        if p2[1] > WIDTH // 2 - h1:  # Cant throw above specified height
            distance_between_points = 50
            n_points = 5
            for i in range(n_points):
                x = p1[0] - p2[0] + (i - n_points//2) * distance_between_points
                h2 = p1[1] - p2[1]
                pygame.draw.circle(screen, (255, 0, 0), (p2[0] + (i - n_points//2) * distance_between_points, p2[1]), 5)

                vec = get_vector(9.8, h1, h2, x, second_root)
                particles.append(Particle(screen, Vector2(p1), vec))


        clock.tick(60)
        [p.update() for p in particles]
        #pygame.draw.circle(screen, (255, 0, 0), p2, 5)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
