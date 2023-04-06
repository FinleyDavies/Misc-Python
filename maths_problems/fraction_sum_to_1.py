from fractions import Fraction as Frac
from time import sleep as sl
import sys

sys.setrecursionlimit(2024)

LIMIT = 2023
frac_dict = dict()


# Even if you greedily take the largest decomposition of a fraction, into other fractions,
# it may be that a smaller option uses more unique fractions, which could mean fewer duplicates, and more overall


def decomposition1(c_sum, depth, size):
    print(c_sum, depth, size, LIMIT)
    for i in range(depth, LIMIT):
        print(i)
        inverse = Frac(1, i)
        new_sum = Frac(inverse + Frac(c_sum))
        if new_sum.numerator > new_sum.denominator:
            return 0
        frac_dict[new_sum] = [c_sum, inverse, size]
        decomposition1(new_sum, i, size + 1)


def decomposition2(c_sum, depth, components, previous):



    #sl(0.5)
    #print(c_sum, depth, size, LIMIT)
    for i in range(depth, LIMIT-1):
        new_i = LIMIT - i
        inverse = Frac(1, new_i)
        new_sum = Frac(inverse + Frac(c_sum))

        if new_sum.numerator < new_sum.denominator:
            new = components.copy()
            new.add(inverse.denominator)
            decomposition2(new_sum, i + 1, new, components)
        elif float(new_sum) < 1.0000049769415957:
            print(float(new_sum), len(components), components.difference(previous))

    return 0





if __name__ == "__main__":
    decomposition2(0, 0, {0}, {0})

    for k, v in frac_dict.items():
        print(k, v)
