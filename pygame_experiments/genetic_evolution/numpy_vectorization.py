import numpy
import cProfile

from math import sin, cos, pi, atan2, sqrt

from numba import njit
import time


# object: [x, y, direction]
# sensor: [x, y, direction, range, FOV]

# given an array of positions, and sensors, return an array of all objects that are within each sensor's range


# Naive implementation

def get_visible_naive(positions, sensors):
    sensor_data = []

    for x, y, direction, _range, FOV in sensors:
        stimuli = []
        for x2, y2, direction2 in positions:
            # calculate relative position of object
            # if the object is within range and FOV, add it to the list of stimuli
            rel_x, rel_y = x2 - x, y2 - y
            if sqrt(rel_x ** 2 + rel_y ** 2) <= _range:
                if abs(atan2(rel_y, rel_x) - direction) <= FOV / 2:
                    stimuli.append([x2, y2, direction2])
        sensor_data.append(stimuli)
    return sensor_data


def get_visible_naive_no_sqrt(positions, sensors):
    sensor_data = []
    for x, y, direction, _range, FOV in sensors:
        stimuli = []
        for x2, y2, direction2 in positions:
            # calculate relative position of object
            # if the object is within range and FOV, add it to the list of stimuli
            rel_x, rel_y = x2 - x, y2 - y
            if rel_x ** 2 + rel_y ** 2 <= _range ** 2:
                if abs(atan2(rel_y, rel_x) - direction) <= FOV / 2:
                    stimuli.append([x2, y2, direction2])
        sensor_data.append(stimuli)
    return sensor_data


def get_visible_numpy(positions, sensors):
    # vectorize nested for loop
    # calculate relative positions of all objects from each sensor:
    relative_positions = numpy.zeros((len(sensors), len(positions), 4))
    relative_positions[:, :, :2] = positions[:, :2] - sensors[:, numpy.newaxis, :2]
    # calculate distance from each sensor to each object:
    distances = numpy.sqrt(numpy.sum(relative_positions[:, :, :2] ** 2, axis=2))
    distance_mask = distances <= sensors[:, numpy.newaxis, 3]

    # calculate angle from each sensor to each object:
    angles = numpy.arctan2(relative_positions[:, :, 1], relative_positions[:, :, 0])
    angle_mask = numpy.abs(angles - sensors[:, numpy.newaxis, 2]) <= sensors[:, numpy.newaxis, 4] / 2

    # print(distances, distances.shape)
    # print(sensors[:, 3], sensors[:, 3].shape)
    # print(angles, angles.shape)
    # print(sensors[:, 2], sensors[:, 2].shape)

    relative_positions[:, :, 2] = distances
    relative_positions[:, :, 3] = angles

    # create a list of lists of stimuli for each sensor from the original positions array:

    # replace all positions that are not within range or FOV with 0
    relative_positions[~distance_mask | ~angle_mask] = 0

    # relative_positions = relative_positions[distance_mask & angle_mask]
    #print(f"{distances[distance_mask & angle_mask].shape} visible objects")
    return relative_positions


def get_visible_numpy_early_exit(positions, sensors):
    # wip - currently slower

    relative_positions = numpy.zeros((len(sensors), len(positions), 4))
    relative_positions[:, :, :2] = positions[:, :2] - sensors[:, numpy.newaxis, :2]
    distances = numpy.sqrt(numpy.sum(relative_positions[:, :, :2] ** 2, axis=2))
    distance_mask = distances <= sensors[:, numpy.newaxis, 3]
    # where distance_mask is False, set all values in relative_positions to 0
    relative_positions[:, :, 2] = distances
    relative_positions[~distance_mask] = 0

    # early exit if object is not within range
    angles = numpy.where(relative_positions[:, :, 2] == 0, 0,
                         numpy.arctan2(relative_positions[:, :, 1], relative_positions[:, :, 0]))
    angle_mask = numpy.abs(angles - sensors[:, numpy.newaxis, 2]) <= sensors[:, numpy.newaxis, 4] / 2

    relative_positions[:, :, 3] = angles
    relative_positions[~angle_mask] = 0
    #print(f"{distances[distance_mask & angle_mask].shape} visible objects")

    return relative_positions


def get_visible_numpy_optimized(positions, sensors):
    relative_positions = positions[:, numpy.newaxis, :2] - sensors[:, :2]
    visible_positions = numpy.zeros((len(sensors), len(positions), 4))

    distances = numpy.sum(numpy.square(relative_positions[:, :, :2]), axis=2)
    angles = numpy.arctan2(relative_positions[:, :, 1], relative_positions[:, :, 0])

    distance_mask = distances <= numpy.square(sensors[:, 3])
    angle_mask = numpy.logical_and(
        -sensors[:, 4] / 2 <= angles - sensors[:, 2],
        angles - sensors[:, 2] <= sensors[:, 4] / 2,
    )

    visible_positions[distance_mask & angle_mask, :2] = relative_positions[distance_mask & angle_mask]

    visible_positions[distance_mask & angle_mask, 2] = distances[distance_mask & angle_mask]
    visible_positions[distance_mask & angle_mask, 3] = angles[distance_mask & angle_mask]

    #print(f"{distances[distance_mask & angle_mask].shape} visible objects")
    return visible_positions


def get_visible_numpy_optimized_2(positions, sensors):
    relative_positions = positions[:, numpy.newaxis, :2] - sensors[:, :2]
    visible_positions = numpy.zeros((len(sensors), len(positions), 4))

    distances = numpy.sum(numpy.square(relative_positions[:, :, :2]), axis=2)
    angles = numpy.arctan2(relative_positions[:, :, 1], relative_positions[:, :, 0])

    distance_angle_mask = (distances <= numpy.square(sensors[:, 3])) & \
                          (-sensors[:, 4] / 2 <= angles - sensors[:, 2]) & \
                          (angles - sensors[:, 2] <= sensors[:, 4] / 2)

    visible_positions[distance_angle_mask, :2] = relative_positions[distance_angle_mask]

    visible_positions[distance_angle_mask, 2] = distances[distance_angle_mask]
    visible_positions[distance_angle_mask, 3] = angles[distance_angle_mask]

    #print(f"{numpy.count_nonzero(distance_angle_mask)} visible objects")
    return visible_positions

@njit
def get_visible_naive_jit(positions, sensors):
    sensor_data = []
    for x, y, direction, _range, FOV in sensors:
        stimuli = []
        for x2, y2, direction2 in positions:
            # calculate relative position of object
            # if the object is within range and FOV, add it to the list of stimuli
            rel_x, rel_y = x2 - x, y2 - y
            if rel_x ** 2 + rel_y ** 2 <= _range ** 2:
                if abs(atan2(rel_y, rel_x) - direction) <= FOV / 2:
                    stimuli.append([x2, y2, direction2])
        sensor_data.append(stimuli)
    return sensor_data

@njit
def get_visible_naive_no_sqrt_jit(positions, sensors):
    sensor_data = []
    for x, y, direction, _range, FOV in sensors:
        stimuli = []
        for x2, y2, direction2 in positions:
            # calculate relative position of object
            # if the object is within range and FOV, add it to the list of stimuli
            rel_x, rel_y = x2 - x, y2 - y
            if rel_x ** 2 + rel_y ** 2 <= _range ** 2:
                if abs(atan2(rel_y, rel_x) - direction) <= FOV / 2:
                    stimuli.append([x2, y2, direction2])
        sensor_data.append(stimuli)
    return sensor_data


def benchmark(function, *args, maxtime=5, **kwargs):
    start = time.time()
    count = 0
    while time.time() - start < maxtime:
        function(*args, **kwargs)
        count += 1
    duration = time.time() - start
    print(f"{function.__name__}:\nCount:\t\tDuration (s):\t\tAverage (ms):\n"
          f"{count}\t\t\t{round(duration,4)}\t\t\t\t{round(duration / count * 1000, 4)}\n")

def main():
    positions = numpy.multiply(numpy.random.rand(500, 3), numpy.array([1920, 1080, 2 * pi]))
    sensors = numpy.multiply(numpy.random.rand(500, 5), numpy.array([1920, 1080, 2 * pi, 100, 2 * pi]))

    # positions = numpy.array([[0, 0, 30], [1, 1, 0], [2, 3, 2]])
    # sensors = numpy.array([[0, 0, 0, 1, 2 * pi], [0, 1, 0, 2, 2 * pi], [0, 2, 0, 3, 2 * pi]])
    # positions = numpy.array([[0, 0], [1, 1], [2, 3]])
    # sensors = numpy.array([[0, 0], [0, 1]])

    # print('Naive implementation:')
    # cProfile.runctx('get_visible_naive(positions, sensors)', globals(), locals())
    # print('Naive implementation without sqrt:')
    # cProfile.runctx('get_visible_naive_no_sqrt(positions, sensors)', globals(), locals())
    # print('numpy implementation 1:')
    # cProfile.runctx('get_visible_numpy(positions, sensors)', globals(), locals())
    # print('numpy implementation early exit:')
    # cProfile.runctx('get_visible_numpy_early_exit(positions, sensors)', globals(), locals())
    # print('numpy implementation ai:')
    # cProfile.runctx('get_visible_numpy_optimized(positions, sensors)', globals(), locals())
    # print('numpy implementation ai 2:')
    # cProfile.runctx('get_visible_numpy_optimized_2(positions, sensors)', globals(), locals())
    # print('naive no sqrt jit:')
    # cProfile.runctx('get_visible_naive_no_sqrt_jit(positions, sensors)', globals(), locals())

    benchmark(get_visible_naive, positions, sensors)
    benchmark(get_visible_naive_no_sqrt, positions, sensors)
    benchmark(get_visible_numpy, positions, sensors)
    #benchmark(get_visible_numpy_early_exit, positions, sensors)
    benchmark(get_visible_numpy_optimized, positions, sensors)
    benchmark(get_visible_numpy_optimized_2, positions, sensors)
    benchmark(get_visible_naive_jit, positions, sensors)
    benchmark(get_visible_naive_no_sqrt_jit, positions, sensors)







if __name__ == '__main__':
    main()
