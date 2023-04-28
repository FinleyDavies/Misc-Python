import pygame
import numpy
from math import sin, cos, pi, atan2, atan

from pygame import Vector2
from numba import njit


#@njit
def update_goal_heading(organisms):
    new_organisms = organisms.copy()
    inner_organisms = organisms.copy()
    for i, (x, y, direction, team, goal) in enumerate(organisms):
        if team == 0:
            continue
        # if team == 2:
            # print("blue:",round(x,2), round(y, 2), "\n\n")
        # elif team == 1:
            # print("red:",round(x,2), round(y, 2))

        ally_total_x, ally_total_y = 0, 0
        enemy_total_x, enemy_total_y = 0, 0
        ally_heading_x, ally_heading_y = 0, 0
        enemy_heading_x, enemy_heading_y = 0, 0
        any_stimuli = False

        for x2, y2, direction2, team2, goal2 in inner_organisms:
            if team2 == 0 or x == x2 and y == y2:
                continue

            rel_x, rel_y = x2 - x, y2 - y
            relative_angle = atan2(rel_y, rel_x) - direction
            distance_squared = rel_x ** 2 + rel_y ** 2
            # if team == 1:
            #     print(x, y,x2,y2, rel_x, rel_y, direction)
            #     print(organisms[:2])
            #     print("blue" if team == 2 else "red", team2, "relative angle:", round(relative_angle*180/pi, 2))
            if distance_squared <= 50**2:
                # print("organism at", x, y, "is touching organism at", x2, y2)
                # print(organisms[:2])
                if abs(relative_angle) <= pi / 4:
                    any_stimuli = True
                    if team == team2:
                        # print("organism at", x, y, "sees ally at", x2, y2)
                        ally_total_x += rel_x
                        ally_total_y += rel_y
                        ally_heading_x += cos(direction2)
                        ally_heading_y += sin(direction2)
                    else:
                        # print("organism at", x, y, "sees enemy at", x2, y2)
                        enemy_total_x += rel_x
                        enemy_total_y += rel_y
                        enemy_heading_x += cos(direction2)
                        enemy_heading_y += sin(direction2)

        if any_stimuli:
            new_goal = atan2(enemy_total_y, enemy_total_x)
            print("new direction:", round(new_goal*180/pi, 2))
            new_organisms[i][4] = new_goal

        # rotate towards goal:
        diff = (goal - direction) % (2*pi)
        if diff > pi:
            new_organisms[i][2] -= 0.1
        elif diff < pi:
            new_organisms[i][2] += 0.1
        elif abs(diff) < 0.1:
            new_organisms[i][2] = goal.copy()

    return new_organisms







class Organism:
    def __init__(self, sim, index, x=0, y=0, direction=0, team=1):
        self.sim = sim
        self.index = index
        self.x = x
        self.y = y
        self.direction = direction
        self.team = team


    @property
    def x(self):
        return self.sim.organisms[self.index][0]

    @x.setter
    def x(self, value):
        self.sim.organisms[self.index][0] = value

    @property
    def y(self):
        return self.sim.organisms[self.index][1]

    @y.setter
    def y(self, value):
        self.sim.organisms[self.index][1] = value

    @property
    def direction(self):
        return self.sim.organisms[self.index][2]

    @direction.setter
    def direction(self, value):
        self.sim.organisms[self.index][2] = value

    @property
    def team(self):
        return self.sim.organisms[self.index][3]

    @team.setter
    def team(self, value):
        self.sim.organisms[self.index][3] = value


class Simulation:
    def __init__(self, width, height, max_organisms=30):
        self.organisms = numpy.zeros((max_organisms, 5))  # [x, y, direction, team]
        #self.organisms = []
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        self.move_gene = numpy.array([0.1, 0.5, 0, 0.1, 0.5, 0.1, 0.5, 0.5, 0.15, 0.15])
        self.mapped_move_gene = self.lerp_gene(self.move_gene)

        self.speed = 0.5
        self.turn_speed = 0.05
        self.position_update_interval = 1
        self.radius = 10

    def new_organism(self):
        for i, organism in enumerate(self.organisms):
            if organism[3] == 0:
                return Organism(self, i)
        raise Exception("Too many organisms")

    def new_organism_(self):
        self.organisms.append([0, 0, 0, 0, 0])
        return Organism(self, len(self.organisms)-1)

    def populate(self, n_organisms, rect):
        for i in range(n_organisms):
            organism = self.new_organism()
            organism.x = numpy.random.uniform(rect.left, rect.right)
            organism.y = numpy.random.uniform(rect.top, rect.bottom)
            organism.direction = numpy.random.uniform(0, 2 * pi)
            organism.team = numpy.random.randint(1, 3)

    def draw(self, screen):
        for x, y, direction, team, goal in self.get_alive_organisms():
            if team == 1:
                color = (255, 0, 0)
            elif team == 2:
                color = (0, 0, 255)

            pygame.draw.circle(screen, color, (x, y), self.radius)
            pygame.draw.polygon(screen, color, ((x + self.radius*2* cos(direction), y + self.radius*2 * sin(direction)),
                                               (x + self.radius*0.9 * cos(direction + pi / 2), y + self.radius*0.9 * sin(direction + pi / 2)),
                                               (x + self.radius*0.9 * cos(direction - pi / 2), y + self.radius*0.9 * sin(direction - pi / 2))))
            #draw FOV:
            pygame.draw.line(screen, color, (x, y), (x + 50* cos(direction+pi/4), y + 50 * sin(direction+pi/4)))
            pygame.draw.line(screen, color, (x, y), (x + 50* cos(direction-pi/4), y + 50 * sin(direction-pi/4)))
    def get_alive_organisms(self):
        # print(numpy.where(self.organisms[:, 3] != 0)[0])
        return self.organisms[numpy.where(self.organisms[:, 3] != 0)[0]]

    def run(self):
        counter = 0
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.populate(1, pygame.Rect(0, 0, self.width, self.height))
                    elif event.button == 3:
                        self.populate(100, pygame.Rect(0, 0, self.width, self.height))

            self.screen.fill((255, 255, 255))
            self.organisms[0][:2] = pygame.mouse.get_pos()

            self.update_position_vectorised()
            if counter % self.position_update_interval == 0:
                self.update_heading()
                counter = 0

            # set first organism to mouse position:

            self.draw(self.screen)
            pygame.display.flip()
            counter += 1

    def lerp(self, a, b, t):
        return a + (b - a) * t

    def lerp_gene(self, gene):
        ranges = [(0, pi / 2), (0, 2 * pi), (0, 2 * pi), (0, 1), (0, 1), (0, 1), (0, 2 * pi), (0, 2 * pi), (0, 1),
                  (0, 1)]
        return [self.lerp(a, b, t) for (a, b), t in zip(ranges, gene)]

    def bad_code(self):
        random, enemy, friend, r_weight, e_weight, f_weight, e_vel, f_vel, e_vel_weight, f_vel_weight = self.mapped_move_gene

        for i, (x, y, direction, team, goal) in enumerate(self.get_alive_organisms()):
            # rotate towards goal:
            #get the difference in angle between the goal and the current direction:


            visible_rect = pygame.Rect(x - 50, y - 50, 100, 100)
            visible_organisms = numpy.where(
                (self.organisms[:, 0] > visible_rect.left) & (self.organisms[:, 0] < visible_rect.right) & (
                        self.organisms[:, 1] > visible_rect.top) & (self.organisms[:, 1] < visible_rect.bottom))[0]
            visible_organisms = visible_organisms[numpy.where(visible_organisms != i)]

            #new_heading = direction + numpy.random.uniform(-random, random)
            new_heading = direction

            if len(visible_organisms) == 0:
                continue

            visible_team_members = visible_organisms[numpy.where(self.organisms[visible_organisms][:, 3] == team)]
            visible_opponents = visible_organisms[numpy.where(self.organisms[visible_organisms][:, 3] != team)]

            if len(visible_opponents) != 0:
                opponent_relative_positions = self.organisms[visible_opponents][:, :2] - numpy.array([x, y])
                opponent_average_position = numpy.average(opponent_relative_positions, axis=0)
                opponent_relative_direction = numpy.arctan2(opponent_average_position[1], opponent_average_position[0]) - direction
                opponent_relative_headings = numpy.subtract(self.organisms[visible_opponents][:, 2], direction)

                #new_heading += numpy.average(opponent_relative_headings)
                new_heading += numpy.average(opponent_relative_direction + enemy)
                self.organisms[i][4] = new_heading % (2 * pi)

            if len(visible_team_members) != 0:
                team_relative_positions = self.organisms[visible_team_members][:, :2] - numpy.array([x, y])
                team_relative_directions = numpy.arctan2(team_relative_positions[:, 1], team_relative_positions[:, 0])
                team_relative_directions = numpy.subtract(team_relative_directions, direction)
                team_relative_headings = numpy.subtract(self.organisms[visible_organisms][:, 2], direction)

                new_heading += numpy.average(team_relative_headings)
                #self.organisms[i][4] = new_heading % (2 * pi)
                # new_heading += numpy.average(team_relative_directions)
                #self.organisms[i][4] = new_heading % (2 * pi)

            # if len(visible_opponents) != 0 and len(visible_team_members) != 0:
            #     self.organisms[i][4] /= 2


    def update_heading(self):
        #print("updating heading")
        self.organisms = update_goal_heading(self.organisms)


    def update_position_vectorised(self):
        pass


        # x, y, direction, team, goal = self.organisms.T
        # x += numpy.cos(direction) * self.speed
        # y += numpy.sin(direction) * self.speed
        # x = numpy.mod(x, self.width)
        # y = numpy.mod(y, self.height)

        # if abs(goal - direction) <= self.turn_speed:
        #     self.organisms[:, 2] = goal
        # elif 0 < (goal - direction) % (2 * pi) < pi:
        #     self.organisms[:, 2] += self.turn_speed
        #     self.organisms[:, 2] = self.organisms[:, 2] % (2 * pi)
        # else:
        #     self.organisms[:, 2] -= self.turn_speed
        #     self.organisms[:, 2] = self.organisms[:, 2] % (2 * pi)

        # direction_mask = numpy.abs(goal - direction) <= self.turn_speed
        # direction = numpy.where(direction_mask, goal, direction)
        # range_mask_1 = numpy.logical_and(0 < (goal - direction) % (2 * pi), (goal - direction) % (2 * pi) < pi)
        # direction = numpy.where(range_mask_1 & ~direction_mask, direction + self.turn_speed, direction - self.turn_speed)
        #
        # self.organisms[:, 2] = direction % (2 * pi)
        # #self.organisms[:, 4] = goal % (2 * pi)
        # self.organisms[:, 0] = x
        # self.organisms[:, 1] = y


def main():
    sim = Simulation(800, 600)
    sim.populate(2, pygame.Rect(100, 100, 600, 400))
    sim.organisms[0][3] = 1
    sim.organisms[1][3] = 2
    sim.run()


if __name__ == "__main__":
    main()
