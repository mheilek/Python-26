import csv

with open("../transactions.csv", "r", encoding="utf-8") as soubor:
   ctecka = csv.DictReader(soubor, delimiter=";")
   for radek in ctecka:
       value = float(radek["value"])
       if value >= 20000:
           print(radek["from"], "->", radek["to"], "|", value)
           
 