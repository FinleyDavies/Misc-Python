from pygame import Vector2, draw, gfxdraw, Surface
import time
from typing import List, Union, Tuple
import random
import math

from utilities.vector import Vector


class Particle:
    def __init__(self,
                 owner,
                 position: Vector2,
                 direction: float,
                 speed: float,
                 duration: float,
                 size_start: float,
                 size_end: float,
                 colour: Tuple[int],
                 offset: float,
                 age: float = 0,
                 fps: float = 60):

        self.owner = owner
        self.position = position
        self.direction = direction
        self.speed = speed
        self.active_frames = duration * fps
        self.size = size_start
        self.colour = colour
        self.offset = offset

        self.age = age
        self.updates = 0

        self.direction_vector = Vector2.from_polar((speed, direction))

        self.position_step = self.direction_vector * speed * (1 / fps)
        self.size_step = (size_end - size_start) / duration * (1 / fps)

        if self.age > 0:
            self.updates -= 1
            self.update()

    def update(self):
        if self.updates > self.active_frames:
            self.kill()

        self.position += self.position_step
        self.size += self.size_step
        self.updates += 1

    def draw(self):
        screen = self.owner.get_screen()
        mode = self.owner.get_draw_mode()

        if mode == "gfxdraw":
            pass
        elif mode == "draw":
            draw.circle(screen, self.colour, self.position, int(self.size))

    def kill(self):
        self.owner.remove_particle(self)



class ParticleSystemPoint:
    MAX_VELOCITIES = 100
    DEFAULTS = {
        "position": ((0, 0), 0, 100),
        "direction": (0, 360, 720),
        "speed": (10, 5, 10),
        "rate": (20, 0, 10),
        "duration": (1, 0.1, 10),
        "size_start": (5, 1, 2),
        "size_end": (0, 0, 0),
        "colour": ((230, 230, 230), 10, 5),
        "offset": (0, 0, 10)
    }

    def __init__(self,
                 screen: Surface,
                 position: Tuple[Union[Tuple, float]] = (),
                 direction: Tuple[Union[float, int]] = (),
                 speed: Tuple[Union[float, int]] = (),
                 rate: Tuple[Union[float, int]] = (),
                 duration: Tuple[Union[float, int]] = (),
                 size_start: Tuple[Union[float, int]] = (),
                 size_end: Tuple[Union[float, int]] = (),
                 colour: Tuple[Union[Tuple, float]] = (),
                 offset: Tuple[Union[float, int]] = ()):

        def fill_defaults(specified: Tuple, name: str):
            n_args = len(specified)
            return specified + self.DEFAULTS[name][n_args:]

        self.screen = screen
        self.position = fill_defaults(position, "position")
        self.direction = fill_defaults(direction, "direction")
        self.speed = fill_defaults(speed, "speed")
        self.rate = fill_defaults(rate, "rate")
        self.duration = fill_defaults(duration, "duration")
        self.size_start = fill_defaults(size_start, "size_start")
        self.size_end = fill_defaults(size_end, "size_end")
        self.colour = fill_defaults(colour, "colour")
        self.offset = fill_defaults(offset, "offset")
        self.draw_mode = "draw"

        self.start_time = None
        self.previous_emit_time = None

        self.particles = []
        self.total_particles = 0

        self.velocities = []
        self.total_velocities = 0

    def get_screen(self):
        return self.screen

    def get_draw_mode(self):
        return self.draw_mode

    def get_random_velocity(self):
        if self.MAX_VELOCITIES > 0:
            if self.total_particles == self.MAX_VELOCITIES:
                return random.choice(self.velocities)

    def emit(self) -> int:
        if self.start_time is None:
            self.start_time = self.previous_emit_time = time.time()
            return 0

        current_time = time.time()

        dT = current_time - self.previous_emit_time
        n_particles = self.rate[0] * (1 / 60) # dT

        t = 0
        while t < dT:
            p = Particle(self,
                         self.generate_position(),
                         self.generate_direction(),
                         self.generate_speed(),
                         self.generate_duration(),
                         self.generate_size(True),
                         self.generate_size(False),
                         self.generate_colour(),
                         self.generate_offset(),
                         age=dT - t)

            self.add_particle(p)
            t += dT / n_particles

        self.particles += []
        self.total_particles += n_particles

        self.previous_emit_time = current_time

    def update(self):
        for particle in self.particles:
            particle.update()
            particle.draw()

    def add_particle(self, particle: Particle):
        self.particles.append(particle)
        self.total_particles += 1

    def remove_particle(self, particle: Particle):
        self.particles.remove(particle)
        self.total_particles -= 1

    def get_random_value(self, attr: str):
        if attr not in self.DEFAULTS:
            raise TypeError(f"{attr} not a supported attribute")

        value, variance, num_steps = self.__getattribute__(attr)

        if num_steps == 0 or variance == 0:
            return value

        step_size = variance * 2 / num_steps
        if isinstance(value, tuple):
            return tuple([v + random.uniform(-0.5, 0.5) * num_steps * step_size for v in value])
        return value + random.uniform(-0.5, 0.5) * num_steps * step_size

    def generate_position(self):
        return Vector2(self.get_random_value("position"))

    def generate_direction(self):
        return self.get_random_value("direction")

    def generate_speed(self):
        return self.get_random_value("speed")

    def generate_duration(self):
        return self.get_random_value("duration")

    def generate_size(self, start: bool):
        if start:
            return self.get_random_value("size_start")
        return self.get_random_value("size_end")

    def generate_colour(self):
        return self.get_random_value("colour")

    def generate_offset(self):
        return self.get_random_value("offset")


class ParticleSystemPolygon:
    def __init__(self, polygon: List[Vector2]):
        pass


if __name__ == "__main__":
    import pygame
    pygame.init()

    WIDTH, HEIGHT = 600, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    p = ParticleSystemPoint(screen,
                            speed=(20,),
                            direction=(90, 20, 10),
                            rate=(500,),
                            duration=(0.8,),
                            colour=((230, 100, 20), 20))

    p3 = ParticleSystemPoint(screen,
                            speed=(17,),
                            direction=(90, 20, 10),
                            rate=(200,),
                            duration=(0.2,),
                            colour=((120, 20, 200), 20),
                            size_start=(7,),
                            size_end=(4,))

    p2 = ParticleSystemPoint(screen)

    print(f"start pos: {p.generate_position()}")
    print(f"start dir: {p.generate_direction()}")
    print(f"start spe: {p.generate_speed()}")
    print(f"dur: {p.generate_duration()}")
    print(f"start size: {p.generate_size(True)}")
    print(f"end size: {p.generate_size(False)}")
    print(f"colour: {p.generate_colour()}")
    print(f"offset: {p.generate_offset()}")
    print(vars(p))

    clock = pygame.time.Clock()

    running = True
    while running:
        screen.fill((0, 0, 0))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        if pygame.mouse.get_pressed()[0]:
            p.position = (pygame.mouse.get_pos(), 0, 0)
            p.emit()

        if pygame.mouse.get_pressed()[1]:
            p2.position = (pygame.mouse.get_pos(), 0, 0)
            p2.emit()


        if pygame.mouse.get_pressed()[2]:
            p3.position = (pygame.mouse.get_pos(), 0, 0)
            p3.emit()

        p.update()
        p2.update()
        p3.update()
        pygame.display.update()
        clock.tick(60)

    pygame.quit()
