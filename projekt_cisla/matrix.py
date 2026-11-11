import random

def zeros(m, n):
    """
    Function creates empty matrix
    """
    matrix_c = []
    for i in range(m):
            matrix_c.append([])
            for _ in range(n):
                matrix_c[i].append(0)
    return matrix_c

def plus(matrix_a, matrix_b):
    m, n = size_of(matrix_a)
    matrix_c = zeros(m, n)
    for i in range(m):
        for j in range(n):
            matrix_c[i][j] = matrix_a[i][j] + matrix_b[i][j]
    return matrix_c        

def minus(matrix_a, matrix_b):
    matrix_c = zeros(len(matrix_a), len(matrix_a[0]))
    for i in range(len(matrix_c)):
            for j in range(len(matrix_c[i])):
                matrix_c[i][j] = matrix_a[i][j] - matrix_b[i][j]
    return matrix_c    

def eyes(m, n):
    """
    Vygeneruje jednotkovou matici
    """
    matrix = zeros(m, n)
    for i in range(m):
        for j in range(n):
            if i == j:
                 matrix[i][j] = 1
    return matrix

def size_of(matrix):
    "Vraci velikost matice"
    return (len(matrix), len(matrix[0]))

def format(matrix):
     size_m, size_n = size_of(matrix)
     print(f"Size ({size_m}, {size_n})")
     for i in range(size_m):
          for j in range(size_n):
               print(f"{matrix[i][j]}\t", end="")
          print()

def multiply_const(matrix, const):
    m, n = size_of(matrix)
    result = zeros(m, n)
    for i  in range(m):
        for j in range(n):
            result[i][j] = matrix[i][j] * const
    return result

def multiply(matrix_a, matrix_b):
    mA, nA = size_of(matrix_a)
    mB, nB = size_of(matrix_b)
    if nA != mB:
         raise ValueError(f"Matrix A and B can not be multiply.")
    result = zeros(mA, nB)
    for i in range(mA):
         for j in range(nB):
              sum = 0
              for l in range(nA):
                   sum += matrix_a[i][l] * matrix_b[l][j]
              result[i][j] = sum
    return result


def apply(matrix, func):
    m, n = size_of(matrix)
    result = zeros(m, n)
    for i  in range(m):
        for j in range(n):
            result[i][j] = func(matrix[i][j])
    return result

def T(matrix):
    """
    []
    """
    m, n = size_of(matrix)
    result = zeros(n, m)
    for i  in range(m):
         for j in range(n):
              result[j][i] = matrix[i][j]
    return result

def replace_row(matrix, vector, index):
    m, n = size_of(matrix)
    result = zeros(m, n)
    for i in range(m):
         for j in range(n):
              if i == index:
                result[i][j] = vector[j] 
              else:
                result[i][j] = matrix[i][j]
    return result

                   

def replace_collum(matrix, vector, index):
     m, n = size_of(matrix)
     result = zeros(m, n)
     for i in range(m):
        for j in range(n):
         if j == index:
            result[i][j] = vector[i] 
         else:
            result[i][j] = matrix[i][j]
     return result

def determinant(matrix):
    m, n = size_of(matrix)
    if m == 2 and n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[1][0] * matrix[0][1]
    elif m == 3 and n == 3:
        return (matrix[0][0] * matrix[1][1] * matrix[2][2] + 
               matrix[1][0] * matrix[2][1] * matrix[0][2] + 
               matrix[2][0] * matrix[0][1] * matrix[1][2] -
               matrix[0][2] * matrix[1][1] * matrix[2][0] -
               matrix[1][2] * matrix[2][1] * matrix[0][0]-
               matrix[2][2] * matrix[0][1] * matrix[1][0])
    else:
        raise ValueError (f"Matice neni 2x2 nebo 3x3")

def _get_value(matrix, x, y):
    m, n = size_of(matrix)
    if x >= 0 and x < m and y >= 0 and y < n:
        return matrix[x][y] 
    else:
        return 0

def _do_convolution(matrix, x, y, kernel):
    sum = 0
    kernel_size = len(kernel)
    center_index = kernel_size // 2
    for i in range(0 - center_index, center_index + 1):
        for j in range(0 - center_index, center_index + 1):
            sum += _get_value(matrix, x + i, y + j) * kernel[i + center_index][j + center_index] 

    return sum

def convolution(matrix, kernel):
    m, n = size_of(matrix)
    result = zeros(m, n)
    for i in range(m):
        for j in range(n):
            result[i][j] = _do_convolution(matrix, i, j, kernel)
    return result


def multiply_elementwise(matrix_a, matrix_b):
    m, n = size_of(matrix_a)

    if size_of(matrix_a) != size_of(matrix_b):
        raise ValueError("Matrices must have the same dimensions.")

    result = zeros(m, n)

    for i in range(m):
        for j in range(n):
            result[i][j] = matrix_a[i][j] * matrix_b[i][j]

    return result

def gen_random_matrix(m, n):
    result = zeros(m, n)
    for i in range(m):
        for j in range(n):
            result[i][j] = random.uniform(-0.01, 0.01)
    return result

def reshape(image):
    result = zeros(256 * 256, 1)

    for i in range(256):
        for j in range(256):
            result[i * 256 + j][0] = image[i][j]

    return result