import pygame
from numba import njit
import numpy
from enum import Enum
from math import sin, cos, pi, atan2, sqrt


@njit
def get_direction(current_heading, goal_heading, turn_speed):
    diff = goal_heading - current_heading
    if diff > 180:
        diff = goal_heading - current_heading - 360
    elif diff <= -180:
        diff = goal_heading - current_heading + 360

    return min(max(diff, -turn_speed), turn_speed)


class Gene:
    class Mode(Enum):
        CLIP = 0
        WRAP = 1
        BOUNCE = 2

    MAX_NAME_LENGTH = 35

    def __init__(self, name, min_=0, max_=1, weight=0.5, wrap_type=Mode.CLIP):
        assert len(name) <= self.MAX_NAME_LENGTH
        self.name = name
        self.weight = weight
        self.min_ = min_
        self.max_ = max_
        self.wrap_type = wrap_type
        self.linked_genes = set()
        self.linked_genes.add(self)

    def link_gene(self, gene):
        self.linked_genes.add(gene)
        for linked_gene in gene.linked_genes:
            linked_gene.linked_genes = self.linked_genes

        self.rebalance()

    def rebalance(self):
        total_weight = sum(gene.weight for gene in self.linked_genes)
        print(total_weight)
        for gene in self.linked_genes:
            gene.weight /= total_weight

    def alter_gene(self, value):
        self.weight = value
        self.rebalance()

    def get_value(self):
        return self.weight * (self.max_ - self.min_) + self.min_

    def __repr__(self):
        # string = f"{self.name}({round(self.weight, 4)}) {round(self.get_value(), 4)}"
        # sum = 0
        # for gene in self.linked_genes - {self}:
        #     string += f"\n\t{gene.name}({round(gene.weight, 4)}) {round(gene.get_value(), 4)}"
        #     sum += gene.weight

        def draw_bar(weight, value, min_, max_):
            rounded = str(round(value, 4))
            filled = '='*int(weight * 100)
            unfilled = '-'*(100 - int(weight * 100 - 1))

            if len(unfilled) < len(rounded):
                return filled[:-len(rounded)] + rounded + '|' + unfilled

            elif len(unfilled) > len(rounded):
                return filled + '|' + rounded + unfilled[len(rounded):]

            else:
                return filled + '|' + rounded

        string = self.name

        # tabulate so bar lines up by adding spaces until length equal to max name length:
        while len(string) < self.MAX_NAME_LENGTH:
            string += ' '
        string += draw_bar(self.weight, self.get_value(), self.min_, self.max_)
        return string


class Genome:
    def __init__(self, genes):
        self.genes = []
        self.blocks = {}
        self.n_genes = 0
        self.scales = numpy.zeros((self.n_genes, 2))
        for gene in genes:
            self.add_gene(gene)

    def add_gene(self, gene):
        self.genes.append(gene)
        self.n_genes += 1
        self.scales = numpy.append(self.scales, [[gene.min_, gene.max_ - gene.min_]], axis=0)

    def add_block(self, genes, name):
        start_index = self.n_genes
        for gene in genes:
            self.add_gene(gene)
        self.blocks[name] = (start_index, self.n_genes)


    def get_scaled_values(self, values: numpy.array):
        return values * self.scales[:, 0] + self.scales[:, 1]

    def link_gene(self, gene, other_gene, weight=1):
        """Links two genes together, so that when one is changed, the others are changed so the weighted sum is constant.
        """

    def alter_gene(self, gene, value):
        """Changes the value of a gene, and alters the values of all linked genes so that the weighted sum is constant.
        """
        if gene not in self.genes:
            raise ValueError("Gene not in genome")

    @property
    def length(self):
        return self.n_genes

    def __repr__(self):
        string = f"Genome ({self.n_genes}):\n"
        for gene in self.genes:
            string += str(gene) + "\n"

        return string

    def __index__(self, index):
        if isinstance(index, str):
            return self.genes[self.blocks[index][0]:self.blocks[index][1]]
        else:
            return self.genes[index]

class Organism:
    def __init__(self, x, y, genome):
        self.x = x
        self.y = y
        self.heading = 0
        self.genome = genome

class Simulation:
    def __init__(self, width, height, n_organisms, n_food, n_water, genome_default):
        self.organisms = []
        self.genome = genome_default
        self.food = []
        self.water = []
        # numpy array containing positions of all organisms, food and water, and their index in the respective list:
        # [x, y, genome...]
        self.info = numpy.zeros((n_organisms + n_food + n_water, 4 + genome_default.length))

    @njit
    def get_organism_stimuli(self, organism):
        """Returns a list of all objects that this organism can sense"""
        pass

    def draw(self, screen):
        pass


    # stats = ["health", "energy", "speed", "strength", "stamina", "size", "age", "max_age", "max_health", "max_energy", "max_speed", "max_strength", "max_stamina", "max_size"]
    # features = {"memory":["capacity", "duration"], "metabolism":["rate", "efficiency"], "reproduction":["rate", "efficiency"], "movement":["speed", "acceleration", "turning_speed"], "senses":["range", "resolution", "sensitivity"], "attack":["range", "damage", "speed"], "defense":["armor", "regeneration", "speed"], "size":["width", "height", "depth"], "appearance":["color", "texture", "pattern"], "communication":["range", "speed", "bandwidth"], "intelligence":["capacity", "speed", "efficiency"], "social":["range", "speed", "bandwidth"], "emotion":["range", "speed", "bandwidth"], "personality":["range", "speed", "bandwidth"], "morality":["range", "speed", "bandwidth"], "culture":["range", "speed", "bandwidth"], "language":["range", "speed", "bandwidth"], "technology":["range", "speed", "bandwidth"], "religion":["range", "speed", "bandwidth"], "politics":["range", "speed", "bandwidth"], "economy":["range", "speed", "bandwidth"], "education":["range", "speed", "bandwidth"], "entertainment":["range", "speed", "bandwidth"], "art":["range", "speed", "bandwidth"], "science":["range", "speed", "bandwidth"], "philosophy":["range", "speed", "bandwidth"], "religion":["range", "speed", "bandwidth"], "politics":["range", "speed", "bandwidth"], "economy":["range", "speed", "bandwidth"], "education":["range", "speed", "bandwidth"], "entertainment":["range", "speed", "bandwidth"], "art":["range", "speed", "bandwidth"], "science":["range", "speed", "bandwidth"], "philosophy":["range", "speed", "bandwidth"]}


def generate_genes():
    states = ["default"]#, "flee", "attack", "eat", "drink", "rest", "reproduce", "explore", "wander", "idle"]
    stimuli_types = ["enemy", "ally", "food", "water", "shelter"]
    stimuli_attributes = ["heading", "position", "distance", "health", "energy"]
    modifiers = ["angle_offset", "angle_variance"]

    max_eyes = 3


    features = {
        "memory": [("capacity", 0, 10), ("duration", 0, 120)],
        "legs": [("speed", 0, 5), ("injury_discount", 0, 50), ("acceleration", 0, 2)]}
    genes = []
    # Movement genes todo: reduce number of genes - maybe have a single gene for each stimuli type for each state
    for state in states:
        for stimuli_type in stimuli_types:
            if stimuli_type in ["enemy", "ally"]:
                for stimuli_attribute in stimuli_attributes:
                    genes.append(Gene(f"{state}_{stimuli_type}_{stimuli_attribute}_weight"))
                for modifier in modifiers:
                    genes.append(Gene(f"{state}_{stimuli_type}_{modifier}"))

            else:
                genes.append(Gene(f"{state}_{stimuli_type}_position_weight"))

    # Eye genes
    genes.append(Gene("eye_count", 1, max_eyes))
    for eye in range(max_eyes):
        strength = Gene(f"eye_{eye}_strength", 0, 10, 0.1)
        fov = Gene(f"eye_{eye}_fov", 0, 360)
        range_ = Gene(f"eye_{eye}_range", 0, 1000)
        perception = Gene(f"eye_{eye}_perception", 0, 1)
        fov.link_gene(range_)
        fov.link_gene(perception)
        genes.append(strength)
        genes.append(fov)
        genes.append(range_)
        genes.append(perception)

    for name, feature in features.items():
        gene_to_link = Gene(f"{name}_{feature[0][0]}", feature[0][1], feature[0][2])
        genes.append(gene_to_link)
        for feature_name, min_, max_ in feature[1:]:
            gene = Gene(f"{name}_{feature_name}", min_, max_)
            gene_to_link.link_gene(gene)
            genes.append(gene)



    return genes

def main():
    genes = generate_genes()
    genome = Genome(genes)
    print(genome)


if __name__ == "__main__":
    main()
