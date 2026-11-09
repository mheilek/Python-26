import math
from matrix import T, multiply, apply, plus

def signiod(x):
    return 1 / (1 + math.exp(-x))


def neuron_network(
    X
):
    X = T(X)
    W = [
        [0.4, 0.1, 0.3, 0.4, 0.1, 0.5, -0.2], #dog
        [-0.2, -0.2, 0.1, 0.1, 0.1, 0.1, 0.6],
        [0.4, 0.3, 0.5, 0.5, 0.5, 0.3, 0.8]
    ]
    b = T([[0.1, 0.6, 0.1]])

    result = multiply(W, X)
    result = plus(result, b)
    
    return apply(result, signiod)
    
def do_softmax(items):
    items = items[0]
    total_signoid = sum(items)
    result = []
    for i in items:
        result.append(i/total_signoid)
    return result
    
    
if __name__ == "__main__":
    x = [
        [0.75, 1, 1, 1, 1, 1, 0] #priznaky
    ]
    
    Y = (neuron_network(
        x
    ))
    Y = T(Y)
    print(do_softmax(Y))