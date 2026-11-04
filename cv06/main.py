from matrix import plus, zeros, minus, eyes, size_of, format, multiply, convolution
from view import load, numpy_to_list, list_to_numpy, show

    
if __name__ == "__main__":
    kernel = [
        [1, 0, -1],
        [1, 0, -1],
        [1, 0, -1]
    ]
    kernel2 = [
        [1, 1, 1],
        [0, 0, 0],
        [-1, -1, -1]
    ]
    bluer = [
        [1/9, 1/9, 1/9],
        [1/9, 1/9, 1/9],
        [1/9, 1/9, 1/9]
    ]


    image = load("C:\\Users\\matej.heilek\\Desktop\\Python-26-6\\cv06\\image.png")
 
    img = numpy_to_list(image)
    new_img = convolution(img, kernel)
    new_img_2 = convolution(img, kernel2)
    new_img_3 = convolution(img, bluer)
    np_img = list_to_numpy(new_img_3)
    show(np_img)