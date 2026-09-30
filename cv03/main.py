## nactete int ze vstupu a naformatujte ho na hh:mm:ss hour:min:sec

if __name__ == "__main__":
    i = int(input("Zadej cas: "))
    hour = i//3600
    minut = (i % 3600) // (60)
    second = (i % 3600) % (60)
    print(f"{hour}:{minut}:{second}")
