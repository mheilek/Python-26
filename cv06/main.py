from matrix import plus, zeros, minus, eyes, size_of, format, multiply

if __name__ == "__main__":
    matrix_a = [
        [1, 0, 1],
        [0, 1, 0],
        [0, 0, 1]
    ]
    
    matrix_b = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]
    
print(multiply(matrix_a, matrix_b))