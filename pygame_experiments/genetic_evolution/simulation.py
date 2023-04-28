import pygame
import numpy


class Simulation:
    def __init__(self, width, height, n_organisms, n_food, n_water):
        self.organisms = []
        self.food = []
        self.water = []
        # numpy array containing positions of all organisms, food and water, and their index in the respective list:
        # [x, y, type, index]
        self.positions = numpy.zeros((n_organisms + n_food + n_water, 4))

    def draw(self, screen):
        for x, y, type, index in self.positions:
            if type == 0:
                if self.organisms[index].has_stimuli():
                    color = (255, 255, 0)
                else:
                    color = (255, 0, 0)
            elif type == 1:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
            pygame.draw.circle(screen, color, (x, y), 5)

    def get_organism_stimuli(self, organism):
        """Returns a list of all objects that this organism can sense"""
        for sensor in organism.sensors:
            pass
