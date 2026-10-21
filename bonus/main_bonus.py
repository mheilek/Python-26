import csv
from collections import Counter
import string
 
with open("../text.txt", "r", encoding="utf-8-sig") as f:
    text = f.read().lower()
 
vysledek = ""
 
for znak in text:
    if 'a' <= znak <= 'z':
        vysledek += chr((ord(znak) - ord('a') + 11) % 26 + ord('a'))
    else:
        vysledek += znak
 
print(vysledek)
 
pismena = [c for c in text if c.isalpha()]
cetnosti = Counter(pismena)
celkem = len(pismena)
 
for znak, pocet in cetnosti.most_common():
    procenta = pocet / celkem * 100
    print(f"{znak}: {pocet:8} výskytů ({procenta:5.2f} %)")
 
with open("../../vysledek.txt", "w", encoding="utf-8") as f:
    f.write(vysledek)
 