import pygame

screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

r = 10

pos = pygame.Vector2(0, 500 - 2 * r)
g = pygame.Vector2(0, 70)


class Ball:
    def __init__(self, pos: pygame.Vector2, color: str) -> None:
        self.pos = pos.copy()
        self.surf = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, color, (r, r), r)

        self.velocity = pygame.Vector2(100, -100)

    def update_ghast(self, dt: float) -> None:
        self.velocity += g * dt
        self.pos += self.velocity * dt

    def update_andrew(self, dt: float) -> None:
        self.pos += self.velocity * dt + 1 / 2 * g * dt ** 2
        self.velocity += g * dt

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.surf, self.pos)


ghast_ball = Ball(pos, "red")
andrew_ball = Ball(pos, "blue")

running = True
while running:
    dt = clock.tick() / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ghast_ball.update_ghast(dt)
    andrew_ball.update_andrew(dt)

    screen.fill("black")
    ghast_ball.draw(screen)
    andrew_ball.draw(screen)
    pygame.display.flip()

    pygame.display.set_caption(str(andrew_ball.pos - ghast_ball.pos))