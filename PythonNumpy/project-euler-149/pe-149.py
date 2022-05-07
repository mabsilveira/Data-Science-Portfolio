
import numpy as np
from math import ceil


def lagged_fibonacci_generator(num: int):
    """
    For 1 ≤ k ≤ 55: 
        s(k) = [100003 − 200003k + 300007k3] (modulo 1000000) − 500000
    For 56 ≤ k ≤ 4000000:
        s(k) = [s(k-24) + s(k-55) + 1000000] (modulo 1000000) − 500000
    """

    if num <= 55:
        aux = np.arange(num)+1

        return np.remainder(
            100003 - 200003 * aux + 300007 * aux ** 3, 1000000) - 500000

    array = np.empty(num, dtype=int)  # np.int64)
    aux = np.arange(55, dtype=np.int64)+1
    array[:55] = np.remainder(
        100003 - 200003 * aux + 300007 * aux ** 3, 1000000) - 500000

    for i in range((num-55)//23):
        n = 55+23*i
        aux = array[n-24:n-1] + array[n-55:n-55+24-1]
        array[n:n+24-1] = np.remainder(aux+1000000, 1000000) - 500000

    i = (num-55) % 23
    n = num-i
    aux = array[n-24:n-24+i] + array[n-55:n-55+i]
    array[n:] = np.remainder(aux+1000000, 1000000) - 500000

    return array


def lagged_fibonacci_generator_basic(num: int):
    array = np.arange(num, dtype=np.int64)+1
    for i in array:
        if i <= 55:
            array[i-1] = np.remainder(
                100003 - 200003 * i + 300007 * i ** 3, 1000000) - 500000
        else:
            array[i-1] = np.remainder(array[i-1-24] +
                                      array[i-1-55] + 1000000, 1000000) - 500000

    return array


def maximum_sum_subsequence_by_row(matrix: np.array):
    # Horizontal sequences
    nRows, nCols = matrix.shape
    horizontalTensor = np.empty([nRows, nCols+1, nCols], dtype=int)
    for i, row in enumerate(matrix):
        line = row.cumsum()
        horizontalTensor[i] = np.triu(- np.insert(line,
                                                  [0], 0)[:, np.newaxis] + line)
    return horizontalTensor.max()


def batch_maximum_sum_subsequence_by_row(matrix: np.array):
    memNeeded = matrix.shape[0]*(matrix.shape[1]+1) * \
        matrix.shape[1]*matrix.dtype.itemsize/1073741824
    nBatches = ceil(memNeeded/8)
    # print(nBatches)

    maxArray = []
    for i in range(0, matrix.shape[0], matrix.shape[0]//nBatches):
        maxArray.append(maximum_sum_subsequence_by_row(
            matrix[i:i+matrix.shape[0]//nBatches]))

    return max(maxArray)


def maximum_sum_subsequence(matrix: np.array):
    maxArray = []
    # horizontal
    maxArray.append(batch_maximum_sum_subsequence_by_row(matrix))

    # vertical
    maxArray.append(batch_maximum_sum_subsequence_by_row(matrix.transpose()))

    # diagonal
    diagonals = np.empty([2*matrix.shape[0]-3, matrix.shape[0]], dtype=int)
    for i in range(-matrix.shape[0]+2, matrix.shape[0]-1):
        diagonals[i+matrix.shape[0] -
                  2] = np.pad(matrix.diagonal(i), (0, abs(i)))
    maxArray.append(batch_maximum_sum_subsequence_by_row(diagonals))

    # anti-diagonal
    for i in range(-matrix.shape[0]+2, matrix.shape[0]-1):
        diagonals[i+matrix.shape[0] -
                  2] = np.pad(matrix[::-1].diagonal(i), (0, abs(i)))
    maxArray.append(batch_maximum_sum_subsequence_by_row(diagonals))

    return max(maxArray)


if __name__ == '__main__':
    N = 2000

    matrix = np.reshape(lagged_fibonacci_generator(N**2), (N, N))

    s10 = matrix[(10-1)//N][(10-1) % N]
    s100 = matrix[(100-1)//N][(100-1) % N]
    print(f"""lagged_fibonacci_generator check:

    s10 = -393027
    lagged_fibonacci_generator(10) = {s10}
    s100 = 86613
    lagged_fibonacci_generator(100) = {s100}
    """)

    print('matrix', matrix.shape, """
    """)

    print(maximum_sum_subsequence(matrix))
