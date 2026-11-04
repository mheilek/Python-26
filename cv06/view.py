from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def load(cesta):
    img = Image.open(cesta).convert("L")
    matrix = np.array(img)
    return matrix

def show(matrix):
    plt.imshow(matrix, cmap="gray")
    plt.colorbar()
    plt.show()

def numpy_to_list(matrix):
    return matrix.astype(int).tolist()

def list_to_numpy(my_list):
    return np.array(my_list, dtype=int)

