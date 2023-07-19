def max_sub_array(array, k):
    maxi = None
    pos = 0
    for i in range(len(array)-k):
        total = sum(array[i:i+k])
        if maxi is None or total > maxi:
            maxi = total
            pos = i
    return array[pos:pos+k]


def max_sub_array_faster(array, k):
    maxi = sum(array[:k])
    pos = 0
    total = maxi
    for i in range(len(array)-k):
        total -= array[i]
        total += array[i+k]
        if total > maxi:
            maxi = total
            pos = i
    return array[pos+1:pos+k+1]

def sub_array_ge(array, S, smallest=0, v=0):
    length = len(array)
    if sum(array) >= S:
        smallest = min(smallest, length) if smallest != 0 else length
    else:
        return array + [v]
    # remove smallest value from either end:
    if array[0] < array[-1]:
        return sub_array_ge(array[1:], S, smallest, array[1])

    return sub_array_ge(array[:-1], S, smallest, array[-1])

def sub_array_ge_2(array, S):
    window_sum = 0
    start = 0
    k = 0
    for i in range(len(array)):
        window_sum += array[i]
        if window_sum >= S:
            length = i - start
            if k == 0 or k > length:
                k = length
            window_sum -= array[start]
            start += 1







# print(max_sub_array([2,1,5,1,3,2], 3))
# print(max_sub_array_faster([2,1,5,1,3,2], 3))

print(sub_array_ge([1,1,1,1,1,5,6,7,1,1,1,1,1,1,1], 11))
print(sub_array_ge_2([1,1,1,1,1,5,6,1,1,1,1,1,1,1,1], 11))