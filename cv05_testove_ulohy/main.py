def year(number):
    return number % 400 or ((number % 4 == 0) and (number % 100 != 0))

def mean():
    x1 = int(input("1: "))
    x2 = int(input("2: "))
    x3 = int(input("3: "))
    print(f"Vysledek: {(x1 + x2 + x3) / 3}")

def nums():
    n = int(input("Cislo: "))
    for i in range(n):
        print(f"{i + 1}")

def even_nums():
    n = int(input("Cislo: "))
    for i in range(n):
        print(f"{(i % 2 != 0) + i}")

if __name__ == "__main__":
    even_nums()