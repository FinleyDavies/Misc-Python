import pygame
import math
import random
from shapely.geometry import Polygon, Point


class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.weight = 2
        self.color = (0, 255, 255)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.r, self.weight)

    def intersects(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2) < self.r + other.r

    def set_color(self, color):
        self.color = color

    def set_weight(self, weight):
        self.weight = weight

    def move(self, x, y):
        self.x = x
        self.y = y

    def increase_radius(self, r):
        self.r += r
        self.r = min(200, max(10, self.r))


def get_tangents(x1, y1, r1, x2, y2, r2):
    # translated to python with chatgpt from:
    # https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Tangents_between_two_circles
    d_sq = (x1 - x2) ** 2 + (y1 - y2) ** 2
    if d_sq <= (r1 - r2) ** 2:
        return []

    d = math.sqrt(d_sq)
    vx = (x2 - x1) / d
    vy = (y2 - y1) / d

    res = []
    for sign1 in [1, -1]:
        c = (r1 - sign1 * r2) / d

        if c * c > 1.0:
            continue
        h = math.sqrt(max(0.0, 1.0 - c * c))

        for sign2 in [1, -1]:
            nx = vx * c - sign2 * h * vy
            ny = vy * c + sign2 * h * vx

            res.append([x1 + r1 * nx, y1 + r1 * ny, x2 + sign1 * r2 * nx, y2 + sign1 * r2 * ny])

    return res


def circle_line_intersection(cx, cy, cr, x1, y1, x2, y2, lb=True, ub=True):
    dx, dy = x2 - x1, y2 - y1
    A = dx ** 2 + dy ** 2
    B = 2 * (dx * (x1 - cx) + dy * (y1 - cy))
    C = (x1 - cx) ** 2 + (y1 - cy) ** 2 - cr ** 2
    det = B ** 2 - 4 * A * C
    if A == 0:
        # Line is a point
        return []

    if det < 0:
        # No real intersection
        return []
    elif det == 0:
        # One intersection
        t = -B / (2 * A)
        if (not lb or t >= 0) and (not ub or t <= 1):
            x = x1 + t * dx
            y = y1 + t * dy
            return [[x, y]]
        else:
            return []
    else:
        # Two intersections
        intersections = []
        for sign in [-1, 1]:
            t = (-B + sign * math.sqrt(det)) / (2 * A)
            if (not lb or t >= 0) and (not ub or t <= 1):
                x = x1 + t * dx
                y = y1 + t * dy
                intersections.append([x, y])
        return intersections


def get_first_intersection(circles, ray):
    # get the first circle to be intersected by the ray
    first_intersection = (None, None)
    for index, c in enumerate(circles):
        intersections = circle_line_intersection(c[0], c[1], c[2], ray[0], ray[1], ray[2], ray[3], ub=False)
        if intersections:
            for intersection in intersections:
                if first_intersection[0] is None:
                    first_intersection = (intersection, index)
                else:
                    if abs(intersection[0] - ray[0]) < abs(first_intersection[0][0] - ray[0]) or abs(
                            intersection[1] - ray[1]) < abs(first_intersection[0][1] - ray[1]):
                        first_intersection = (intersection, index)
    return first_intersection


def is_visible(target, source, obstacles, screen):
    # calculate all tangents from source to target:
    tangents = get_tangents(source[0], source[1], source[2], target[0], target[1], target[2])
    # check if the target is directly visible
    for t in tangents:
        if get_first_intersection(obstacles, t) == (None, None):
            pygame.draw.line(screen, (0, 255, 0), (t[0], t[1]), (t[2], t[3]), 2)
            return t

    for index, c in enumerate(obstacles):
        tangents = get_tangents(source[0], source[1], source[2], c[0], c[1], c[2])
        for t in tangents:
            # remove current from obstacles to prevent intersection with tangent:
            obstacles_excluding_current = obstacles[:index] + obstacles[index + 1:]
            point, obstacle = get_first_intersection([target] + obstacles_excluding_current, t)
            # draw unsuccessful rays:
            pygame.draw.line(screen, (255, 0, 0), (t[0], t[1]), (t[2], t[3]), 1)
            if point is not None and obstacle == 0:
                pygame.draw.line(screen, (0, 255, 0), (t[0], t[1]), point, 2)
                return t

    # repeat the process for the target:
    for index, c in enumerate(obstacles):
        tangents = get_tangents(target[0], target[1], target[2], c[0], c[1], c[2])
        for t in tangents:
            # remove current from obstacles to prevent intersection with tangent:
            obstacles_excluding_current = obstacles[:index] + obstacles[index + 1:]
            point, obstacle = get_first_intersection([source] + obstacles_excluding_current, t)
            # draw unsuccessful rays:
            pygame.draw.line(screen, (255, 0, 0), (t[0], t[1]), (t[2], t[3]), 2)
            if point is not None and obstacle == 0:
                pygame.draw.line(screen, (0, 255, 0), (t[0], t[1]), point, 2)
                return t

    # start checking tangents between obstacles:
    for index, c in enumerate(obstacles):
        for index2, c2 in enumerate(obstacles):
            if index != index2:
                tangents = get_tangents(c[0], c[1], c[2], c2[0], c2[1], c2[2])
                for t in tangents:
                    obstacles_excluding_current = [ob for i, ob in enumerate(obstacles) if i != index and i != index2]
                    point1, obstacle1 = get_first_intersection([source, target] + obstacles_excluding_current, t)
                    # cast ray in other direction:
                    point2, obstacle2 = get_first_intersection([source, target] + obstacles_excluding_current,
                                                               [t[2], t[3], t[0], t[1]])
                    # if obstacles are source and target, success:
                    if obstacle1 is None or obstacle2 is None:
                        pygame.draw.line(screen, (255, 0, 0), (t[0], t[1]), (t[2], t[3]), 2)
                        continue
                    if obstacle1 + obstacle2 == 1:  # one obstacle is source and one is target
                        # false positive when obstacles are intersecting source and target
                        # if both intersection points are on the same side of the line, it is a false positive:
                        if (point1[0] - t[0]) * (point2[0] - t[0]) > 0 and (point1[1] - t[1]) * (
                                point2[1] - t[1]) > 0:
                            pygame.draw.line(screen, (255, 0, 0), (t[0], t[1]), (t[2], t[3]), 2)
                            continue
                        pygame.draw.line(screen, (0, 255, 0), (t[0], t[1]), point1, 2)
                        pygame.draw.line(screen, (0, 255, 0), (t[2], t[3]), point2, 2)
                        return t


def main():
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True
    radius = 100
    position = (200, 200)
    # create list of 10 random circles:

    source = Circle(200, 200, 100)
    source.set_color((0, 255, 0))
    target = Circle(300, 200, 100)
    target.set_color((255, 0, 0))
    circles = []
    for i in range(10):
        circles.append(Circle(random.randint(0, 800), random.randint(0, 600), random.randint(10, 100)))

    selected = None
    last_selected = source

    print(
        "Press space to add a random circle, scroll to change radius, click and drag to move, press backspace to remove last selected")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    circles.append(Circle(random.randint(0, 800), random.randint(0, 600), random.randint(10, 100)))
                elif event.key == pygame.K_BACKSPACE:
                    circles.remove(last_selected)
                    last_selected = source
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for c in circles + [source, target]:
                        if math.sqrt((c.x - event.pos[0]) ** 2 + (c.y - event.pos[1]) ** 2) < c.r:
                            last_selected.set_weight(2)
                            last_selected = c
                            selected = c
                            selected.set_weight(4)

                if event.button == 4 and last_selected is not None:
                    last_selected.increase_radius(10)
                if event.button == 5 and last_selected is not None:
                    last_selected.increase_radius(-10)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selected = None

        if selected is not None:
            delta = pygame.mouse.get_rel()
            selected.move(selected.x + delta[0], selected.y + delta[1])
        screen.fill((30, 30, 30))
        pygame.mouse.get_rel()
        position = pygame.mouse.get_pos()

        # get tangents
        tangents = get_tangents(source.x, source.y, source.r, target.x, target.y, target.r)
        poly = Polygon(((tangents[0][0], tangents[0][1]), (tangents[1][0], tangents[1][1]),
                        (tangents[1][2], tangents[1][3]), (tangents[0][2], tangents[0][3])))

        obstacles = []
        for c in circles:
            circle = Point(c.x, c.y).buffer(c.r)
            if poly.intersects(circle):
                c.set_color((255, 0, 255))
                obstacles.append((c.x, c.y, c.r))
            else:
                c.set_color((0, 255, 255))
        for c in circles + [source, target]:
            c.draw(screen)

        los = is_visible((target.x, target.y, target.r), (source.x, source.y, source.r), obstacles, screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
