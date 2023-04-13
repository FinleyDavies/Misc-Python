from pygame import Vector2, draw, gfxdraw, Surface
import time
from typing import List, Union, Tuple
import random
import math

from utilities.vector import Vector

from object_observer import Trackable, Mediator, Observer
from observer_testing import ObserverApp
import tkinter as tk
import threading


class Particle:
    def __init__(self,
                 owner,
                 position: Vector2,
                 direction: float,
                 speed: float,
                 duration: float,
                 size_max: float,
                 size_min: float,
                 colour: Tuple[int],
                 offset: float,
                 age: float = 0,
                 fps: float = 60):


        self.owner = owner
        self.position = position
        self.direction = direction
        self.speed = speed
        self.active_frames = duration * fps
        self.size_max = size_max
        self.size_min = size_min
        self.colour = colour
        self.offset = offset

        self.size = size_max
        self.age = age
        self.updates = 0

        self.direction_vector = Vector2.from_polar((speed, direction))

        self.size_function = lambda x: x
        self.position_function = lambda x: x

        self.position_step = self.direction_vector * speed * (1 / fps)
        self.size_step = (size_min - size_max) / duration * (1 / fps)

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

        size = self.size_function(self.size)

        if mode == "gfxdraw":
            gfxdraw.circle(screen, int(self.position[0]), int(self.position[1]), int(size), self.colour)
        elif mode == "draw":
            draw.circle(screen, self.colour, self.position, int(self.size))

    def kill(self):
        self.owner.remove_particle(self)


class ParticleSystemPoint:
    MAX_VELOCITIES = 100
    DEFAULTS = {
        "position": ((0, 0), (0, 0), 100),
        "direction": (0, 360, 720),
        "speed": (10, 5, 10),
        "rate": (20, 0, 10),
        "duration": (1, 0.1, 10),
        "size": ((5, 0), (1, 0), 2),
        "colour": ((230, 230, 230), (10, 10, 10), 5),
        "offset": (0, 0, 10)
    }

    def __init__(self,
                 screen: Surface,
                 position: Tuple[Union[Tuple, float]] = (),
                 direction: Tuple[Union[float, int]] = (),
                 speed: Tuple[Union[float, int]] = (),
                 rate: Tuple[Union[float, int]] = (),
                 duration: Tuple[Union[float, int]] = (),
                 size: Tuple[Union[float, int]] = (),
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
        self.size = fill_defaults(size, "size")
        self.colour = fill_defaults(colour, "colour")
        self.offset = fill_defaults(offset, "offset")
        self.draw_mode = "gfxdraw"

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

    def set_velocity(self, velocity: Tuple[int]):
        """Changes speed and direction using a velocity vector"""
        speed, direction = Vector2(*velocity).as_polar()
        self.speed = (speed,) + self.speed[1:]
        self.direction = (direction,) + self.direction[1:]

    def emit(self) -> int:
        if self.start_time is None:
            self.start_time = self.previous_emit_time = time.time()
            return 0

        current_time = time.time()

        dT = (1/60) #current_time - self.previous_emit_time
        n_particles = self.rate[0] * (1 / 60)  # dT

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
            raise ValueError(f"{attr} not a supported attribute")

        value, variance, num_steps = self.__getattribute__(attr)

        if num_steps == 0 or variance == 0:
            return value

        #(value, variance)
        if isinstance(value, tuple):
            return tuple([v + int((random.random() - 0.5) * num_steps) / num_steps * variance[i] * 2 for i, v in enumerate(value)])
        return value + int((random.random() - 0.5) * num_steps) / num_steps * variance * 2

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
            return self.get_random_value("size")[0]
        return self.get_random_value("size")[1]

    def generate_colour(self):
        return self.get_random_value("colour")

    def generate_offset(self):
        return self.get_random_value("offset")


class ParticleSystemPolygon:
    def __init__(self, polygon: List[Vector2]):
        pass

def tkinter_thread(observer: Observer):
    root = tk.Tk()

    app = ObserverApp(observer, root)

    app.pack(side="top", fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    import pygame

    pygame.init()

    WIDTH, HEIGHT = 600, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def fade_in_out(t, min_value, max_value):
        return -abs(2 * -t + 1) * (max_value - min_value) + max_value

    system1 = ParticleSystemPoint(screen,
                            speed=(20,),
                            direction=(90, 20, 20),
                            rate=(5000,),
                            duration=(0.5,),
                            colour=((230, 100, 21), (20, 20, 20)),
                            size=((7, 4),),
                            )

    system3 = ParticleSystemPoint(screen,
                             speed=(17,),
                             direction=(90, 17, 10),
                             rate=(2000,),
                             duration=(0.2,),
                             colour=((120, 120, 230), (20, 20, 20)),
                             size=((7, 4),))

    system2 = ParticleSystemPoint(screen,
                             rate=(1,))

    # print("random values:")
    # print(f"start pos: {p.generate_position()}")
    # print(f"start dir: {p.generate_direction()}")
    # print(f"start spe: {p.generate_speed()}")
    # print(f"dur: {p.generate_duration()}")
    # print(f"start size: {p.generate_size(True)}")
    # print(f"end size: {p.generate_size(False)}")
    # print(f"colour: {p.generate_colour()}")
    # print(f"offset: {p.generate_offset()}")
    # print(vars(p))

    mediator = Mediator()
    p = Trackable.from_object(system1, "red particles")
    p2 = Trackable.from_object(system2, "white_particles")
    p3 = Trackable.from_object(system3, "blue_particles")
    mediator.add_trackable(p)
    mediator.add_trackable(p2)
    mediator.add_trackable(p3)
    observer = Observer(mediator)

    observer_thread = threading.Thread(target=tkinter_thread, args=(observer,))
    observer_thread.start()

    clock = pygame.time.Clock()
    previous_mouse_pos = pygame.mouse.get_pos()
    mouse_vel = (0, 0)

    running = True
    while running:
        screen.fill((0, 0, 0))

        current_mouse_pos = pygame.mouse.get_pos()
        mouse_vel = tuple([x-y for x, y in zip(current_mouse_pos, previous_mouse_pos)])
        new_vel = tuple([x+y for x, y in zip(mouse_vel, tuple(Vector2.from_polar((20, 90))))])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        if pygame.mouse.get_pressed()[0]:
            p.position = (pygame.mouse.get_pos(), 0, 0)
            p.set_velocity(new_vel)
            p.emit()

        if pygame.mouse.get_pressed()[1]:
            p2.position = (pygame.mouse.get_pos(), (WIDTH//2, HEIGHT//2), 100)
            p2.emit()

        if pygame.mouse.get_pressed()[2]:
            p3.position = (pygame.mouse.get_pos(), 0, 0)
            p3.emit()

        p.update()
        p2.update()
        p3.update()

        previous_mouse_pos = current_mouse_pos
        pygame.display.update()
        clock.tick(60)

    pygame.quit()
