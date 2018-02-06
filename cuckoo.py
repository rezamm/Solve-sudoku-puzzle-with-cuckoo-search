from problem import inputMatrix
from random import uniform
from random import randint
import math
import numpy as np
import copy
import matplotlib.pyplot as plt
import time

init = np.array(inputMatrix)
init = init - 1


def levy_flight(u):
    return math.pow(u, -1.0 / 3.0)


def rand_f():
    return uniform(0.0001, 0.9999)


def swap(box, idx1, idx2):
    box[idx1[0], idx1[1]], box[idx2[0], idx2[1]] = box[idx2[0], idx2[1]], box[idx1[0], idx1[1]]
    return box


def get_initial_nests(nest_count):
    nests = []
    boxes = define_big_boxes()
    for _ in range(nest_count):
        s = np.copy(init)

        # create each box
        for box_idx in range(9):
            b = s[boxes[box_idx][0][0]:boxes[box_idx][0][1], boxes[box_idx][1][0]:boxes[box_idx][1][1]]
            b = np.reshape(b, [-1])

            for idx in range(9):
                if b[idx] == -2:
                    while True:
                        rnd = int(np.random.randint(0, 9, 1))
                        if not rnd in b:
                            b[idx] = rnd
                            break

            b = np.reshape(b, [3, 3])
            s[boxes[box_idx][0][0]:boxes[box_idx][0][1], boxes[box_idx][1][0]:boxes[box_idx][1][1]] = b
        nests.append((copy.copy(s), calculate_fitness(s)))
        s = None

    return nests


def calculate_fitness(nest):
    f = 0

    # rows
    for row in range(9):
        for num in range(9):
            if not (num in nest[row, :]):
                f += 1
    # columns
    for col in range(9):
        for num in range(9):
            if not (num in nest[:, col]):
                f += 1
    return f


def define_big_boxes():
    boxes = [
        ([0, 3], [0, 3]),
        ([3, 6], [0, 3]),
        ([6, 9], [0, 3]),
        ([0, 3], [3, 6]),
        ([3, 6], [3, 6]),
        ([6, 9], [3, 6]),
        ([0, 3], [6, 9]),
        ([3, 6], [6, 9]),
        ([6, 9], [6, 9]),
    ]
    return boxes


def short_fly(nest):
    boxes = define_big_boxes()
    idx = int(np.random.randint(0, 9, 1))

    # swap two indexes in a square
    new_box = copy.copy(nest[boxes[idx][0][0]:boxes[idx][0][1], boxes[idx][1][0]:boxes[idx][1][1]])
    init_box = init[boxes[idx][0][0]:boxes[idx][0][1], boxes[idx][1][0]:boxes[idx][1][1]]

    # get two unconstraint indexes
    while True:
        idx1 = np.random.randint(0, 3, [2])
        if init_box[idx1[0], idx1[1]] == -2:
            break

    while True:
        idx2 = np.random.randint(0, 3, [2])
        if (init_box[idx2[0], idx2[1]] == -2) & (not np.array_equal(idx1, idx2)):
            break

    new_box = swap(new_box, idx1, idx2)

    nest[boxes[idx][0][0]:boxes[idx][0][1], boxes[idx][1][0]:boxes[idx][1][1]] = new_box
    return (nest, calculate_fitness(nest))


def long_fly(nest):
    boxes = define_big_boxes()
    box_idx = int(np.random.randint(0, 9, 1))

    s = np.copy(init)
    new_box = s[boxes[box_idx][0][0]:boxes[box_idx][0][1], boxes[box_idx][1][0]:boxes[box_idx][1][1]]
    new_box = np.reshape(new_box, [-1])

    for idx in range(9):
        if new_box[idx] == -2:
            while True:
                rnd = int(np.random.randint(0, 9, 1))
                if not rnd in new_box:
                    new_box[idx] = rnd
                    break

    new_box = np.reshape(new_box, [3, 3])

    nest[boxes[box_idx][0][0]:boxes[box_idx][0][1], boxes[box_idx][1][0]:boxes[box_idx][1][1]] = new_box
    return (nest, calculate_fitness(nest))


def long_fly_end(nest):
    for i in range(int(np.random.randint(1, 4, 1))):
        nest = (short_fly(nest))[0]
    return (nest, calculate_fitness(nest))


def remove_duplicates(nests):
    new_nests = []
    for i in range(len(nests)):
        is_exist = False
        for j in range(len(new_nests)):
            if np.array_equal(nests[i][0], new_nests[j][0]):
                is_exist = True
                break
        if not is_exist:
            new_nests.append(copy.copy(nests[i]))
    return new_nests


if __name__ == "__main__":
    start_time = time.time()

    numNests = 100
    nests = []

    pc = int(0.05 * numNests)
    pa = int(0.6 * numNests)

    maxGen = 5000 * 5

    # initialize
    nests = get_initial_nests(numNests)
    nests.sort(key=lambda tup: tup[1])

    fitnesses = []
    t_s = []

    # main body
    for t in range(maxGen):

        cuckooNest = nests[randint(0, pc)]
        if levy_flight(rand_f()) > 1.7:
            if t < int(0.5 * maxGen):
                cuckooNest = long_fly(copy.copy(cuckooNest[0]))
            else:
                cuckooNest = long_fly_end(copy.copy(cuckooNest[0]))
        else:
            cuckooNest = short_fly(copy.copy(cuckooNest[0]))

        randomNestIndex = randint(0, numNests - 1)
        if nests[randomNestIndex][1] > cuckooNest[1]:
            nests[randomNestIndex] = cuckooNest

        for b_idx in range(numNests - pa, numNests):
            nests[b_idx] = long_fly(nests[b_idx][0])

        nests = remove_duplicates(nests)
        nests_count = len(nests)
        # print('Duplicates:{}'.format(numNests - nests_count))

        # create new for replace duplicates
        if numNests > nests_count:
            nests.extend(get_initial_nests(numNests - nests_count))

        nests.sort(key=lambda tup: tup[1])

        if nests[0][1] == 0:
            print('Goal Found!')
            break

        if (t + 1) % 200 == 0:
            print('Gen:{} - best fitness:{}'.format(t + 1, nests[0][1]))
            print(nests[0][0])
            print('nests count:{}'.format(nests_count))

        fitnesses.append(nests[0][1])
        t_s.append(t + 1)

    print("CUCKOO's SOLUTION")
    print(nests[0])

    end_time = time.time()

    print('The algorithm takes {:1.0f} seconds to find solution...'.format(end_time - start_time))

    """"""
    plt.figure(1)
    plt.subplot(211)
    plt.plot(t_s, fitnesses, 'bo', markersize=1)
    plt.show()

