from random import random

def get_color():
    value = random() * 100
    if value <= 3:
        return 2
    elif value <= 51.5:
            return 0
    else:
         return 1

def start_game():
    user_bilance = 1_000
    print("Welcome to casino")
    while True:
      i = input(f"Select your bet ({user_bilance} eur):")
      if not i.isnumeric():
        continue
      bet = int(i)
      if bet > user_bilance:
        print(f"nesmí být větší než {user_bilance}")
        continue
      print("Select color:")
      print("\t\t0 - Red")   # 48.5%
      print("\t\t1 - White") # 48.5%
      print("\t\t2 - Green") # 3%
      print("\t\t9 - leave game")
      s = input("Select: ")
      if not s.isnumeric():
        continue
      selection = int(s)
      if selection == 9:
        return
      elif selection not in [0, 1, 2, 9]:
        print("Wrong input")
        continue
      elif selection == get_color():
          user_bilance = user_bilance + bet * 2
          print("Win")
      else:
          print("Lose")
          user_bilance = user_bilance - bet
    

if __name__ == "__main__":
    start_game()
