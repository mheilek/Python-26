from random import random

total_in = 0
total_tries = 0

for _ in range(1000):
    x = random() - 0.5
    y = random() - 0.5

    size = (x ** 2 + y **2) **(0.5)

    if size <= 0.5:
        total_in = total_in + 1
        
    total_tries = total_tries + 1
    
print((total_in / total_tries) * 4)