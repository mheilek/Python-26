from matrix import plus, apply, multiply, multiply_const, multiply_elementwise, minus, zeros, gen_random_matrix, T
import math
import random

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def sigmoid_derivative_matrix(A):
    return apply(
        A,
        lambda x: x * (1 - x)
    )


def forward(X, W1, B1, W2, B2):

    Z1 = plus(multiply(W1, X), B1)
    A1 = apply(Z1, sigmoid)

    Z2 = plus(multiply(W2, A1), B2)
    A2 = apply(Z2, sigmoid)

    return Z1, A1, Z2, A2


def backward(X, Y, A1, A2, W2, learning_rate):

    # Výstupní vrstva
    dZ2 = multiply_elementwise(
        minus(A2, Y),
        sigmoid_derivative_matrix(A2)
    )

    dW2 = multiply(dZ2, T(A1))
    dB2 = dZ2

    # Skrytá vrstva
    dA1 = multiply(T(W2), dZ2)

    dZ1 = multiply_elementwise(
        dA1,
        sigmoid_derivative_matrix(A1)
    )

    dW1 = multiply(dZ1, T(X))
    dB1 = dZ1

    # Aktualizace parametrů
    W1 = minus(W1, multiply_const(dW1, learning_rate))
    B1 = minus(B1, multiply_const(dB1, learning_rate))

    W2 = minus(W2, multiply_const(dW2, learning_rate))
    B2 = minus(B2, multiply_const(dB2, learning_rate))

    return W1, B1, W2, B2


def train_step(X, Y, W1, B1, W2, B2, learning_rate):

    # FORWARD
    Z1, A1, Z2, A2 = forward(X, W1, B1, W2, B2)

    # BACKWARD
    W1, B1, W2, B2 = backward(
        X, Y, A1, A2, W2, learning_rate
    )

    return W1, B1, W2, B2

def train(training_data, epochs, learning_rate,
          W1, B1, W2, B2):

    for epoch in range(epochs):

        random.shuffle(training_data)

        total_loss = 0

        for path, label in training_data:

            X = load_image(path)

            Y = zeros(10, 1)
            Y[label][0] = 1

            # Forward pro výpočet chyby
            Z1, A1, Z2, A2 = forward(
                X, W1, B1, W2, B2
            )

            # Loss
            for i in range(10):
                error = A2[i][0] - Y[i][0]
                total_loss += 0.5 * error ** 2

            # Backward
            W1, B1, W2, B2 = backward(
                X, Y, A1, A2,
                W1, B1, W2, B2,
                learning_rate
            )

        print(
            f"Epoch {epoch + 1}/{epochs}, "
            f"Loss: {total_loss / len(training_data):.6f}"
        )

    return W1, B1, W2, B2

def load_image():
    # TODO 
    pass

def load_training_data():
    # TODO  
    pass

if __name__ == "__main__":
    INPUT_SIZE = 256 * 256
    HIDDEN_SIZE = 128
    OUTPUT_SIZE = 10

    W1 = gen_random_matrix(HIDDEN_SIZE, INPUT_SIZE)
    W2 = gen_random_matrix(OUTPUT_SIZE, HIDDEN_SIZE)

    B1 = zeros(HIDDEN_SIZE, 1)
    B2 = zeros(OUTPUT_SIZE, 1)

    training_data = load_training_data()
    W1, B1, W2, B2 = train(
        training_data,
        epochs=100,
        learning_rate=0.0001,
        W1=W1,
        B1=B1,
        W2=W2,
        B2=B2
    )