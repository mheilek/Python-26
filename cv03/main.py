## nactete int ze vstupu a naformatujte ho na hh:mm:ss hour:min:sec
def time_format():
    i = int(input("Zadej cas: "))
    hour = i//3600
    minut = (i % 3600) // (60)
    second = (i % 3600) % (60)
    print(f"{hour}:{minut}:{second}")

## automat co rozmeni prachy
## 5000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1
def money_xchange():
    i = int(input("Zadej penize: "))
    pettis = i//5000
    i = i -(pettis * 5000)
    dvoutis = (i % 5000) // 2000
    i = i -(dvoutis * 2000)
    tisic = (i % 2000 ) // 1000
    i = i -(tisic * 1000)
    petset = (i % 1000 ) // 500
    i = i -(petset * 500)
    dveste = (i % 500 ) // 200
    i = i -(dveste * 200)
    sto = (i % 200 ) // 100
    i = i -(sto * 100)
    pade = (i % 100 ) // 50
    i = i -(pade * 50)
    dvacet = (i % 50 ) // 20
    i = i -(dvacet * 20)
    deset = (i % 20 ) // 10
    i = i -(deset * 10)
    pet = (i % 10 ) // 5
    i = i -(pet * 5)
    dva = (i % 5 ) // 2
    i = i -(dva * 2)
    jedna = (i % 2 ) // 1
    print(f"{pettis}x5000:{dvoutis}x2000:{tisic}x1000:{petset}x500:{dveste}x200:{sto}x100:{pade}x50:{dvacet}x20:{deset}x10:{pet}x5:{dva}x2:{jedna}x1")

def money_xchange_v2():
    i = int(input("Zadej penize: "))
    money = [5000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1]
    for item in money:
        count = i // item
        i = i - (item*count)
        print(f"{item}:{count}x")  
if __name__ == "__main__":
    money_xchange_v2()