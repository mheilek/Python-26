import math
#2.5
def year(number):
    return number % 400 or ((number % 4 == 0) and (number % 100 != 0))
#1.5
def mean():
    x1 = int(input("1: "))
    x2 = int(input("2: "))
    x3 = int(input("3: "))
    print(f"Vysledek: {(x1 + x2 + x3) / 3}")
#3.1
def nums():
    n = int(input("Cislo: "))
    for i in range(n):
        print(f"{i + 1}")
#3.5
def odd_sum():
    n = int(input("Cislo: "))
    soucet = 0
    for i in range(n):
        if i % 2 != 0:
            soucet = soucet + i
    print(soucet)
#3.2
def backwards():
    n = int(input("Cislo: "))
    for i in range(n):
        print(f"{n-i}")
#3.6
def nasobilka():
    n = int(input("Cislo: "))
    for i in range(10):
        print(f"{n*(i+1)}")
#7.1
def minimum():
    n = int(input("Cislo: "))
    min = n
    while n != -1:
        if min > n:
            min = n
        n = int(input("Cislo: "))
    print(f"min: {min}")
#3.3
def soucet():
    n = int(input("Cislo: "))
    sum = (n*(n+1)) / 2
    print(soucet)  
#3.4
def even_nums():
    n = int(input("Cislo: "))
    soucet = 0
    for i in range(n):
        if i % 2 == 0:
            soucet = soucet + i
    print(soucet)        
#4.1
def factorial():
    fact = 1
    n = int(input("Cislo: "))
    for i in range(n):
        fact = fact * (i+1)  
    print(f"{fact}")

def factorial_for_combi(n):
    fact = 1
    for i in range(n):
        fact = fact * (i+1)  
    return fact
#5.1
def combi_num():
    n = int(input("Cislo: "))
    k = int(input("Cislo: "))
    print(factorial_for_combi(n) / (factorial_for_combi(k) * factorial_for_combi(n-k)))
#4.2
def factorial_recursion(number):
    if number <= 0:
        return 1
    return factorial_recursion((number - 1)) * number
#2.1
def odd_or_even():
    n = int(input("Cislo: "))
    if n % 2 == 0:
        return True
    return False
#15.1
def obdelnik():
    a = int(input("Cislo: "))
    b = int(input("Cislo: "))
    o = 2*(a+b)
    s = a*b
    print(f"obvod: {o}, obsah: {s}")
#15.2
def kruh():
    r = float(input("Cislo: "))
    o = 2 * math.pi * r
    s = math.pi * (r ** 2)
    print(f"obvod: {o}, obsah: {s}")
#2.4
def biggest():
    a = int(input("Cislo: "))
    b = int(input("Cislo: "))
    c = int(input("Cislo: "))
    highest = max (a,b,c)
    print(f"nejvyssi je {highest}")
#15.3
def pythagor():
    a = int(input("Cislo: "))
    b = int(input("Cislo: "))
    print( ((a ** 2) + (b ** 2)) ** 0.5)
#7.3
def prumer():
    N = int(input("Pocet cisel: "))
    nums = []
    for i in range(N):
        number = int(input(f"Zadej {i+1}. cislo:  "))
        nums.append(number)
    print(sum(nums) / len(nums))
#7.5
def pocetcifer():
    N = int(input("Pocet cisel: "))
    lst = []
    while N != 0:
        lst.append(N % 10)
        N = N // 10
    print(len(lst)) # 7.6 print(sum(lst)) 7.7 print(lst)
#9.1
def NSD():
    a = int(input("Cislo: "))
    b = int(input("Cislo: "))  
    r = 1
    while b != 0:
        a, b = b, a % b
    print(a)
def NSD_NSN(a,b):
    while b != 0:
        a, b = b, a % b
    return(a)
#9.2
def NSN():
    a = int(input("Cislo: "))
    b = int(input("Cislo: "))
    print(+(a * b) / NSD_NSN(a,b))
#11.1
def delka_retezce():
    text = (input("Cislo: "))
    print(len(text))
#11.3 
def palindrom():
    text = (input("Cislo: "))
    pal = text[::-1]
    if pal == text:
        print("Palindrom")
    else:
        print("Neny palindrom")

#11.4
def samohlasky():
    pocet = 0
    text = (input("Texst: "))
    lst = ["a","e","i","o","u","y"]
    for i in range(len(text)):
        for j in range(len(lst)):
            if text[i] == lst[j]:
                pocet = pocet + 1
    print(pocet)

#11.5
def znaky():
    counter = 0
    text = (input("Texst: "))
    dct = {}
    for i in text:
        if i in dct.keys():
            counter = dct[1]
        else:
            dct[i] = 1
    print(dct)

# 12.1
def soucet_seznam():
    N = (input("Cislo: "))
    numbers = []
    for i in N.split():
        numbers.append(int(i))
    print(sum(numbers))
# 12.3
def otocit_seznam():
    N = (input("Cislo: "))
    numbers = []
    for i in N.split():
        numbers.append(int(i))
    print(numbers[::-1])
#12.4
def duplicita():
    N = (input("Cislo: "))
    number = []
    for i in N.split():
        a = int(i)
        if a not in number:
            number.append(a)
    print(number)
#12.2
def maxmin():
    N = (input("Cislo: "))
    number = []
    min = float("inf")
    max = float("-inf")
    for i in N.split():
        a = int(i)
        if a > max:
            max = a
        if a < min:
            min = a
            
    print(f"amx {max} min {min}")
if __name__ == "__main__":
    maxmin()