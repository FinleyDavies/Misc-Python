import numpy
import matplotlib.pyplot as plt
import time


# create arrays of random points of size 1000, 10000, 100000, 1000000
# split each array into sub arrays of size 100
# calculate a transformation on the points in each sub array, and each array and time it
# compare the time taken per point for each array size
# plot the results on a graph for each array size

TRANSLATION = numpy.array([10, -5])
ROTATION = 55
N_TIMES = 100

def tranform_naive(array):
    array[:, 0] = numpy.cos(ROTATION) * array[:, 0] - numpy.sin(ROTATION) * array[:, 1]
    array[:, 1] = numpy.sin(ROTATION) * array[:, 0] + numpy.cos(ROTATION) * array[:, 1]

    array[:, 0] += TRANSLATION[0]
    array[:, 1] += TRANSLATION[1]

def make_homogeneous(array):
    return numpy.hstack((array, numpy.ones((array.shape[0], 1))))
def transform_matrix(homogeneous_points):
    transformation = numpy.array([[numpy.cos(ROTATION), -numpy.sin(ROTATION), TRANSLATION[0]],
                                    [numpy.sin(ROTATION), numpy.cos(ROTATION), TRANSLATION[1]],
                                    [0, 0, 1]])
    return homogeneous_points @ transformation

def check_on_screen(array):
    # returns a boolean array of points that are on screen
    return numpy.logical_and(array[:, 0] > 0, array[:, 0] < 1000)

def to_fps(time):
    fps = time
    #fps = 1 / time
    return fps



def main():
    # create arrays of random points of size 1000, 10000, 100000, 1000000
    sizes = [2000*i for i in range(1, 100)]
    sizes += [100000+100000*i for i in range(1, 9)]
    print(sizes)
    arrays = [numpy.random.rand(size, 2) for size in sizes]

    # split each array into sub arrays of size 100
    sub_arrays = [numpy.split(array, len(array) / 100) for array in arrays]

    # calculate a transformation on the points in each sub array, and each array and time it
    # compare the time taken per point for each array size
    # plot the results on a graph for each array size
    fig, ax = plt.subplots()
    for array, sub_array, size in zip(arrays, sub_arrays, sizes):
        print(f"array size: {array.shape}, size of sub arrays: {sub_array[0].shape}, number of sub arrays: {len(sub_array)}")

        # start = time.perf_counter()
        # for sub in sub_array:
        #     tranform_naive(sub)
        # end = time.perf_counter()
        # print(f"array size: {size}, time taken for sub arrays: {end - start}")
        # ax.scatter(size, end - start, color='blue')

        # start = time.perf_counter()
        # tranform_naive(array)
        # end = time.perf_counter()
        # print(f"array size: {size}, time taken for array: {end - start}")
        # ax.scatter(size, end - start, color='red')

        new = make_homogeneous(array)
        print(new)
        new_sub_array = [make_homogeneous(sub) for sub in sub_array]

        avg = 0
        for i in range(N_TIMES):
            start = time.perf_counter()
            for sub in new_sub_array:
                transform_matrix(sub)
            end = time.perf_counter()
            avg += end - start
        avg /= N_TIMES
        print(f"array size: {size}, time taken for matrix: {avg}")
        ax.scatter(size, to_fps(avg), color='orange')

        avg = 0
        for i in range(N_TIMES):
            start = time.perf_counter()
            transform_matrix(new)
            end = time.perf_counter()
            avg += end - start
        avg /= N_TIMES
        print(f"array size: {size}, time taken for matrix: {avg}")
        ax.scatter(size, to_fps(avg), color='green')

        # start = time.perf_counter()
        # check_on_screen(array)
        # end = time.perf_counter()
        # print(f"array size: {size}, time taken for check on screen: {end - start}")
        # ax.scatter(size, to_fps(end-start), color='purple')


    #ax.set_xscale('log', base=10)
    plt.show()


if __name__ == "__main__":
    main()