
import csv
from collections import Counter

transakce = []

with open("../transactions.csv", encoding="utf-8") as file:
    reader = csv.DictReader(file, delimiter=";")

    for row in reader:
        od = row["from"].strip()
        komu = row["to"].strip()
        castka = float(row["value"].replace(",", "."))

        transakce.append((od, komu, castka))

print("Počet načtených transakcí:", len(transakce))

podezrele = Counter()

for i in range(len(transakce)):
    od1, komu1, castka1 = transakce[i]

    for j in range(i + 1, len(transakce)):
        od2, komu2, castka2 = transakce[j]

        if (
            od1 == komu2
            and komu1 == od2
            and castka1 == castka2
        ):
            dvojice = tuple(sorted([od1, komu1]))
            podezrele[(dvojice, castka1)] += 1

print("\nPodezřelé shody:")

nalezeno = False

for ((osoba1, osoba2), castka), pocet in podezrele.most_common():
    print(
        f"{osoba1} <-> {osoba2}: "
        f"{castka} Kč, počet shod: {pocet}"
    )
    nalezeno = True

if not nalezeno:
    print("Nenašly se žádné shody.")
    print("Zkontroluj názvy sloupců a data v CSV.")
