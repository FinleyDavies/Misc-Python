# a numpy vectorized array of 100000 points, representing each particle, polygon, or drawn object in the world
# a transformation of each point can be done in one operation, taking ~0.00083 seconds
# each game object can own a portion of the array, and its own transformations can be applied each frame -
# eg a particle system can own 5000 points and have a radial spread transformation applied each frame

# optimising:
#   each object (particle system, polygon, sprites) should add or remove themselves from the array as they are
#   within or outside the screen


import numpy as np


class GameObjectArray:
    """stores contiguous lists of points representing all polygons, and particle objects that are to be transformed by
    the camera and drawn to the screen"""

    def __init__(self, max_points=100000):
        self.max_points = max_points
        self.points = np.zeros((max_points, 2), dtype=np.float32)
        self.points_count = 0
        self.start_indices = np.zeros(max_points,
                                      dtype=np.int32)  # same length as points, in case all objects only have 1 point
        self.objects = []

    def add_points(self, points, owner):
        """adds points to the end of the array, and returns the index of the first point"""
        if self.points_count + len(points) > self.max_points:
            raise ValueError("too many points to add")
        start = self.points_count
        self.points[start:start + len(points)] = points
        self.points_count += len(points)
        self.start_indices.append(start)
        return start

    def remove_points(self, start, count):
        """removes points from the array, starting at the given index"""
        self.points[start:start + count] = self.points[self.points_count - count:self.points_count]
        self.points_count -= count

    def transform(self, transform):
        """transforms all points in the array by the given transform"""
        return transform(self.points[:self.points_count])

    @classmethod
    def get_within(cls, points, rect):
        """returns a boolean array indicating which points are within the given rectangle"""
        return np.logical_and(np.logical_and(points[:, 0] >= rect.left, points[:, 0] <= rect.right),
                              np.logical_and(points[:, 1] >= rect.top, points[:, 1] <= rect.bottom))



class GameObject:
    """a game object that can be added to the game object array"""

    def __init__(self, array, size):
        self.array = array
        self.size =size
        self.start = None

    def add_points(self, points):
        """adds points to the array, and returns the index of the first point"""
        self.start = self.array.add_points(points, self)
        self.count = len(points)

    def remove_points(self):
        """removes points from the array"""
        self.array.remove_points(self.start, self.count)
        self.start = None
        self.count = None
