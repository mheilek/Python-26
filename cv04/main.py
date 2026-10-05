#array = [1, 2, 3, 4, 5]

#array.append("caus")

#print(array[-1])
#print(array)
#del array[1]
#print(array)

#for i in range(10):
#    print (i)


def prime_number(number):
    i = number ** 0.5
    while i - 1 > 1:
        if number % i == 0:
            return False
        i = i - 1
    return True

def factorial(number):
    result = 1
    index = 1
    while index < number:
        result = result * number
        index += 1
    return result


def factorial_recursion(number):
    if number < 0:
        return 1
    return factorial_recursion(number - 1) * number

def fibbonachi(number):
    num1 = 0
    num2 = 1
    for _ in range(number):
        num3 = num1 + num2
        num2 = num1
        num1 = num3
    return num3
        

def fibbonachi_recursion(number):
    if number == 0 or number == 1:
        return 1
    return fibbonachi_recursion(number - 1) + fibbonachi_recursion(number - 2)
    
    
def combination_number(n, k):
    return factorial_recursion(n) / (factorial_recursion(k) * factorial_recursion((n - k)))
    

def pascal_triangle(line_index):
    for i in range(line_index + 1):
        print(combination_number(line_index, i))

if __name__ == "__main__":
#    list = []
#    number = None
#    while number is None or number != -1:
#        number = int(input("Zadej cislo: "))
#        if number == -1:
#            break
#        list.append(number)
#    
#    print(f"Max value {max(list)}")
#    print(f"Min value {min(list)}")
#    print(f"Mean value {sum(list)/len(list)}")
    print(fibbonachi(1))
    print(fibbonachi_recursion(10))