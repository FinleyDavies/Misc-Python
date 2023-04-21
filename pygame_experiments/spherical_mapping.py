import pygame
from pygame.locals import *

from math import sin, cos, tan, pi, sqrt, floor, ceil
import numpy as np

from trackable import *
from gui import ObserverApp

WIDTH, HEIGHT = 640, 480
RADIUS = 100


class SphericalMapping:
    """can be instantiated with a surface, filename, or shader function, converts a vector to a pixel on the surface"""

    def __init__(self, surface=None, filename=None, shader=None):
        self.surface = surface
        self.filename = filename
        self.shader = shader

    def get_pixel(self, vector):
        pass

    def generate_surface(self, width, height):
        if not self.shader:
            raise Exception("No shader function provided")

        surface = pygame.Surface((width, height))
        xstep, ystep = 2 / width, 2 / height
        x, y = -1, -1
        while x < 1:
            while y < 1:
                vector = self.get_vector(x, y)
                pixel = self.shader(x, y)
                surface.set_at((x, y), pixel)
                y += ystep
            x += xstep

    def get_vector(self, x, y):
        """converts a 2d coordinate to a 3d vector, where x and y are in the range [-1, 1],
        and the vector is a point on the unit sphere"""
        pass


def draw_sphere(radius, color1, color2, steps=60):
    surf = pygame.Surface((radius * 2, radius * 2))
    surf.fill((0, 0, 0))
    colour_step = (color2[0] - color1[0], color2[1] - color1[1], color2[2] - color1[2])
    colour = color1
    for i in range(steps):
        pygame.draw.circle(surf, colour, (radius, radius), int(radius * cos(i / steps * pi / 2)))
        colour = (
            colour[0] + colour_step[0] / steps, colour[1] + colour_step[1] / steps, colour[2] + colour_step[2] / steps)
    return surf


def rotate_vector(vector, axis, angle):
    """Rotates a vector around an axis by an angle in radians"""
    axis = np.asarray(axis)
    axis = axis / sqrt(np.dot(axis, axis))
    a = cos(angle / 2)
    b, c, d = -axis * sin(angle / 2)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    rotation_matrix = np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                                [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                                [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])
    return np.dot(rotation_matrix, vector)


def get_orthogonal_vector(vector):
    """returns any vector that has a 0 dot product with the input vector"""


def vec_to_rgb(vector):
    """converts a 3d vector to an rgb tuple, where each component is in the range [0, 255]"""
    if vector[0] == 0 and vector[1] == 0 and vector[2] == 0:
        return 0, 0, 0
    return int((vector[0] + 1) * 127), int((vector[1] + 1) * 127), int((vector[2] + 1) * 127)


def create_normal_sphere(radius=100, steps=120, screen=None, offset1=0, offset2=0, size=2):
    if screen is None:
        surf = pygame.Surface((radius * 2 + 2, radius * 2 + 2))
    else:
        surf = screen

    offset1 *= pi / 180
    offset2 *= pi / 180

    vec = np.array([-1, 0, 0])
    vec = rotate_vector(vec, np.array([0, 1, 0]), offset1)
    vec = rotate_vector(vec, np.array([1, 0, 0]), offset2)

    axis1 = np.array([0, 0, 1])
    axis1 = rotate_vector(axis1, np.array([0, 1, 0]), offset1)
    axis1 = rotate_vector(axis1, np.array([1, 0, 0]), offset2)
    axis2 = np.array([-1, 0, 0])
    axis2 = rotate_vector(axis2, np.array([0, 1, 0]), offset1)
    axis2 = rotate_vector(axis2, np.array([1, 0, 0]), offset2)

    angle1 = 0
    angle2 = 0
    vec2 = vec3 = vec
    min_delta = 360 / steps
    max_delta = 360
    delta = max_delta
    center = pygame.Vector2(surf.get_width() / 2 + 1, surf.get_height() / 2 + 1)

    def interpolate_steps(angle):
        return abs(sin(angle * pi / 180)) * steps or 1

    def to_radians(angle):
        return angle * pi / 180

    def get_2d_vector(vector):
        vec2d = pygame.Vector2(vec3[0], vec3[1])
        return center + vec2d * radius

    # pygame.draw.circle(surf, (255, 0, 0), get_2d_vector(vec2), 3)
    while floor(angle1) <= 181:
        vec2 = rotate_vector(vec, axis1, to_radians(angle1))
        angle2 = 0
        inner_steps = interpolate_steps(angle1)
        while floor(angle2) <= 181:
            vec3 = rotate_vector(vec2, axis2, to_radians(angle2))
            pygame.draw.circle(surf, vec_to_rgb(vec3), get_2d_vector(vec3), size)
            angle2 += 360 / inner_steps

        angle1 += 180 / steps

    # pygame.draw.circle(surf, (255, 0, 0), get_2d_vector(vec2), 3)

    return surf


def create_normal_sphere2(radius):
    normal = np.zeros((radius * 2, radius * 2, 3))
    for x in range(radius * 2):
        for y in range(radius * 2):
            if (x - radius) ** 2 + (y - radius) ** 2 > radius ** 2:
                continue
            z = sqrt(max(0, radius ** 2 - (x - radius) ** 2 - (y - radius) ** 2))
            rgb = vec_to_rgb(np.array([x - radius, y - radius, z]) / radius)
            normal[x, y] = rgb
    return pygame.surfarray.make_surface(normal.astype(np.uint8))



def create_normal_sphere2_vectorised(radius, axis=-1):
    tracked_axis = -1
    x_coords = np.arange(radius * 2)
    y_coords = np.arange(radius * 2)
    x, y = np.meshgrid(x_coords, y_coords)

    point_3d = np.stack([x, y, np.zeros_like(x)], axis=tracked_axis) - np.array([radius, radius, 0])
    distance = np.linalg.norm(point_3d, axis=tracked_axis)
    z = np.sqrt(np.maximum(0, radius ** 2 - distance ** 2))
    point_3d[..., 2] = z
    sphere_normal = point_3d / radius

    # normal = np.array([vec_to_rgb(vec) for vec in sphere_normal.reshape(-1, 3)])
    normal = np.clip(sphere_normal * 127 + 127, 0, 255).astype(np.uint8)
    normal[distance > radius] = 0

    return pygame.surfarray.make_surface(normal.reshape(radius * 2, radius * 2, 3).astype(np.uint8))


def initialise_gui():
    def run_gui(observer):
        import tkinter as tk
        root = tk.Tk()
        app = ObserverApp(observer, master=root)
        app.pack()
        root.mainloop()

    mediator = Mediator()
    o = Observer(mediator)
    threading.Thread(target=run_gui, args=(o,)).start()
    return mediator


@track_vars("tracked_axis")
def main():
    mediator = initialise_gui()
    tracked_axis = -1
    angle1, angle2 = 360, 360
    import random

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    # normal_map = create_normal_sphere(radius=RADIUS, steps=360, offset1=angle1, offset2=angle2, size=1)
    normal_map2 = create_normal_sphere2(radius=RADIUS)
    normal_map = create_normal_sphere2_vectorised(RADIUS)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # dt = clock.tick(60)
        screen.fill((0, 0, 0))

        # normal_map = create_normal_sphere(radius=RADIUS, steps=360, offset1=angle1, offset2=angle2, size=1)
        # normal_map2 = create_normal_sphere2(radius=RADIUS)
        normal_map = create_normal_sphere2_vectorised(RADIUS, tracked_axis)
        pos = pygame.mouse.get_pos()
        screen.blit(normal_map, (pos[0] - RADIUS, pos[1] - RADIUS))

        # screen.blit(normal_map, (WIDTH // 2 - 2.5 * RADIUS, HEIGHT // 2 - RADIUS))
        # screen.blit(normal_map2, (WIDTH // 2 + RADIUS // 2, HEIGHT // 2 - RADIUS))

        # create_normal_sphere(radius=RADIUS, steps=50, screen=screen, offset1=angle1, offset2=angle2)

        pygame.display.update()


if __name__ == "__main__":
    main()
    pygame.quit()
