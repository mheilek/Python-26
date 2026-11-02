#generuje prazdne matiec
def zeros(m, n):
    matrix_c = []
    for i in range(m):
        matrix_c.append([])
        for j in range(n):
            matrix_c[i].append(0)
    return matrix_c

def plus(matrix_a, matrix_b):
    matrix_c = zeros(len(matrix_a), len(matrix_b))
    for i in range(len(matrix_a)):
        matrix_c.append([])
        for j in range(len(matrix_a[i])):
            matrix_c[i][j] = matrix_a[i][j] + matrix_b[i][j]
    return matrix_c

def minus(matrix_a, matrix_b):
    matrix_c = zeros(len(matrix_a), len(matrix_b))
    for i in range(len(matrix_a)):
        matrix_c.append([])
        for j in range(len(matrix_a[i])):
            matrix_c[i][j] = matrix_a[i][j] - matrix_b[i][j]
    return matrix_c
#generace jednotkove matice
def eyes(m, n):
    matrix = zeros(m, n)
    for i in range(m):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1
    return matrix

def size_of(matrix):
    return (len(matrix), len(matrix[0]))

def format(matrix):
    print(size_of(matrix))
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(matrix[i][j], end=" ")
        print()
        
def T(matrix):
    m, n = size_of(matrix)
    result = zeros(n, m)
    for i in range(m):
        for j in range(n):
            result[j][i] = matrix[i][j]
    return result

def apply(matrix, func):
    m, n = size_of(matrix)
    result = zeros(n, m)
    for i in range(m):
        for j in range(n):
            result[i][j] = func(matrix[i][j])
    return result

def multiply_const(matrix, const):
    m, n = size_of(matrix)
    result = zeros(n, m)
    for i in range(m):
        for j in range(n):
            result[i][j] = matrix[i][j] * const
    return result            

def multiply(matrix_a, matrix_b):
    mA, nA = size_of(matrix_a)   
    mB, nB = size_of(matrix_b)   
    if nA != nB:
        print("Nejde to")
    result = zeros(mA, nB)
    for i in range(mA):
        for j in range(nB):
            sum = 0
            for l in range(nA):
                sum += matrix_a[i][l] * matrix_b[l][i]
            result[mA][nB] = sum