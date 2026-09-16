import subprocess
import time
import re
import os
import sys
import random

def play_roulette():
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_path = os.path.join(current_dir, "main.py")

    print(f"[Bot] Spouštím hru z: {main_path}")

    process = subprocess.Popen(
        [sys.executable, main_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd=current_dir
    )

    def send_command(cmd):
        process.stdin.write(f"{cmd}\n")
        process.stdin.flush()
        time.sleep(0.8)

    try:
        buffer = ""
        current_selection = 0
        color_names = {0: "Red (Červená)", 1: "White (Bílá)", 2: "Green (Zelená)"}

        while process.poll() is None:
            char = process.stdout.read(1)
            if not char:
                break
            
            buffer += char

            # Pokud hra chce sázku
            if "Select your bet" in buffer:
                match = re.search(r"Select your bet \((\d+) eur\):", buffer)
                if match:
                    balance = int(match.group(1))

                    if balance <= 0:
                        print("\n[Bot] Zůstatek je 0 eur! Konec hry.")
                        send_command("9")
                        break

                    # Vyšší sázky pro 1000 eur (např. 50 až 300 eur, maximálně kolik zbývá)
                    max_bet = min(300, balance)
                    min_bet = min(50, balance)
                    bet_amount = random.randint(min_bet, max_bet)

                    # Náhodný výběr barvy (0: Red, 1: White, 2: Green)
                    current_selection = random.choice([0, 1, 2])

                    print(f"\n----------------------------------------")
                    print(f"[Bot] Zůstatek: {balance} eur | Sázím: {bet_amount} eur na {color_names[current_selection]}")
                    
                    buffer = ""
                    send_command(str(bet_amount))

            # Pokud hra chce vybrat barvu
            elif "Select:" in buffer:
                buffer = ""
                send_command(str(current_selection))

            # Zachycení výsledku (Win / Lose) a vypsání podrobností
            elif "Win" in buffer or "Lose" in buffer:
                # Počkáme na konec řádku s výsledkem
                result_line = ""
                while True:
                    c = process.stdout.read(1)
                    if not c or c == "\n":
                        break
                    result_line += c
                
                full_result = ("Win" if "Win" in buffer else "Lose") + result_line.strip()
                print(f"[Výsledek kola]: {full_result}")
                buffer = ""

    except Exception as e:
        print(f"Chyba: {e}")
    finally:
        process.terminate()
        print("\n[Bot] Skript byl ukončen.")

if __name__ == "__main__":
    play_roulette()