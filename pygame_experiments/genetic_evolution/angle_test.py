import pygame
from math import sin, cos, radians, degrees, atan2, sqrt, acos
import random
from numba import njit
import numpy

SPEED = 10
TURN_SPEED = 5

def get_direction_(current_heading, goal_heading, turn_speed):
    """Returns the direction in which an object should turn to get from current_heading to goal_heading"""
    if abs(current_heading - goal_heading) <= turn_speed:
        return 0
    elif current_heading < goal_heading:
        if goal_heading - current_heading <= 180:
            return turn_speed
        else:
            return -turn_speed
    else:
        if current_heading - goal_heading <= 180:
            return -turn_speed
        else:
            return turn_speed

@njit
def get_direction(current_heading, goal_heading, turn_speed):
    diff = goal_heading - current_heading
    if diff > 180:
        diff = diff - 360
    elif diff <= -180:
        diff = diff + 360

    if abs(diff) <= turn_speed:
        return diff


    return -turn_speed if diff < 0 else turn_speed

@njit
def update_headings(objects, mouse_x, mouse_y):
    new_objects = []
    for x, y, heading, goal in objects:
        goal_heading = degrees(atan2(mouse_y - y, mouse_x - x))
        new_heading = (heading + get_direction(heading, goal_heading, 5)) % 360
        x, y = x + cos(radians(new_heading)), y + sin(radians(new_heading))
        new_objects.append((x, y, new_heading, goal_heading))

    return new_objects

@njit
def get_direction_numpy(current_heading, goal_heading, turn_speed):
    diff = goal_heading - current_heading
    diff = numpy.where(diff > 180, diff - 360, diff)
    diff = numpy.where(diff <= -180, diff + 360, diff)
    return numpy.where(numpy.abs(diff) <= turn_speed, 0, numpy.where(diff < 0, -turn_speed, turn_speed))

@njit
def update_headings_numpy(objects, mouse_x, mouse_y, mode=0):
    x, y, heading, goal, c1, c2, c3 = objects.T
    goal_heading = numpy.degrees(numpy.arctan2(mouse_y - y, mouse_x - x))
    new_heading = numpy.mod(heading + get_direction_numpy(heading, goal_heading, TURN_SPEED), 360)
    if mode == 0:
        x, y = x + numpy.cos(numpy.radians(new_heading)) * SPEED, y + numpy.sin(numpy.radians(new_heading)) * SPEED
    else:
        x, y = x - numpy.cos(numpy.radians(new_heading)) * SPEED, y - numpy.sin(numpy.radians(new_heading)) * SPEED
    return numpy.stack((x, y, new_heading, goal_heading, c1, c2, c3), axis=1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    clock = pygame.time.Clock()
    objects = [(random.randint(0, 800), random.randint(0, 600), 0, random.randint(0, 360),
                random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(10000)]
    objects = numpy.array(objects)

    mode = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mode = (mode + 1) % 2

        screen.fill((0, 0, 0))
        for x, y, heading, goal, c1, c2, c3 in objects:
            pygame.draw.circle(screen, (c1,c2,c3), (x, y), 5)
            pygame.draw.line(screen, (c1,c2,c3), (x, y), (x + 10 * cos(radians(heading)), y + 10 * sin(radians(heading))))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        objects = update_headings_numpy(objects, mouse_x, mouse_y, mode)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()