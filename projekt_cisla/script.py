import os
from collections import defaultdict

import cv2
import pymupdf
import numpy as np


# ==================================================
# NASTAVENI CEST
# ==================================================

# Vloz soubor "Scanned Document.pdf" do stejne slozky
# jako tento Python skript.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "Scanned Document.pdf")

# PNG obrazky se ulozi do teto slozky vedle skriptu.
OUTPUT_DIR = os.path.join(BASE_DIR, "vysledne_cislice")


# ==================================================
# NASTAVENI DATASETU
# ==================================================

ROWS = 10
COLS = 10

OUTPUT_SIZE = 256
DIGIT_SIZE = 200
DPI = 300

# Kolik procent sirky/vysky bunky odriznout z kazde strany.
# Tím se odstrani mrizka a ramecky bunek.
CELL_INSET = 0.12


def order_points(points):
    """Seradi 4 rohy: levy horni, pravy horni, pravy dolni, levy dolni."""
    points = np.asarray(points, dtype=np.float32)
    result = np.zeros((4, 2), dtype=np.float32)

    sums = points.sum(axis=1)
    diffs = np.diff(points, axis=1).reshape(-1)

    result[0] = points[np.argmin(sums)]   # levy horni
    result[2] = points[np.argmax(sums)]  # pravy dolni
    result[1] = points[np.argmin(diffs)]  # pravy horni
    result[3] = points[np.argmax(diffs)] # levy dolni

    return result


def find_grid_and_warp(rgb):
    """Najde vnejsi ramecek tabulky a narovna ji na ctverec."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    height, width = gray.shape

    # Zvvyrazneni tmavych car tabulky.
    binary = cv2.threshold(
        gray, 160, 255, cv2.THRESH_BINARY_INV
    )[1]

    horizontal = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(
            cv2.MORPH_RECT, (max(25, width // 30), 1)
        )
    )

    vertical = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(
            cv2.MORPH_RECT, (1, max(25, height // 30))
        )
    )

    lines = cv2.bitwise_or(horizontal, vertical)
    joined = cv2.dilate(
        lines,
        cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)),
        iterations=2
    )

    contours, _ = cv2.findContours(
        joined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Vyber nejvetsi oblast odpovidajici tabulce.
    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > width * 0.40 and h > height * 0.30:
            candidates.append(contour)

    if not candidates:
        raise RuntimeError(
            "Nepodarilo se najit tabulku. Zkontroluj kvalitu stranky PDF."
        )

    contour = max(candidates, key=cv2.contourArea)
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

    if len(approx) == 4:
        corners = approx.reshape(4, 2)
    else:
        # Zalozni reseni pro lehce deformovane nebo sikme stranky.
        rect = cv2.minAreaRect(contour)
        corners = cv2.boxPoints(rect)

    source = order_points(corners)

    # Narovnana tabulka bude mit 1000 x 1000 pixelu.
    size = 1000
    destination = np.array([
        [0, 0],
        [size - 1, 0],
        [size - 1, size - 1],
        [0, size - 1]
    ], dtype=np.float32)

    transform = cv2.getPerspectiveTransform(source, destination)
    warped = cv2.warpPerspective(rgb, transform, (size, size))

    return warped


def prepare_digit(cell):
    """Odstrani pozadi, oreze cislici a vlozi ji doprostred 256x256."""
    gray = cv2.cvtColor(cell, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    binary = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # Najdi tmave tahy cislice.
    coords = cv2.findNonZero(255 - binary)

    if coords is None:
        return None

    x, y, w, h = cv2.boundingRect(coords)

    if w < 3 or h < 3:
        return None

    digit = binary[y:y + h, x:x + w]

    # Zachovej pomer stran a nastav nejdelsi rozmer na 200 px.
    scale = DIGIT_SIZE / max(w, h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    interpolation = (
        cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    )
    digit = cv2.resize(
        digit, (new_w, new_h), interpolation=interpolation
    )

    canvas = np.full(
        (OUTPUT_SIZE, OUTPUT_SIZE), 255, dtype=np.uint8
    )

    x_offset = (OUTPUT_SIZE - new_w) // 2
    y_offset = (OUTPUT_SIZE - new_h) // 2

    canvas[
        y_offset:y_offset + new_h,
        x_offset:x_offset + new_w
    ] = digit

    return canvas



    
def process_pdf():

    if not os.path.isfile(PDF_PATH):
        print("PDF soubor nebyl nalezen:")
        print(PDF_PATH)
        return

    document = pymupdf.open(PDF_PATH)

    print(f"\nPDF obsahuje {len(document)} stran.")
    print("Zpracovávám celé PDF...")

    # Vytvoření hlavní výstupní složky
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Počítadla jsou mimo cyklus stránek,
    # takže číslování pokračuje napříč celým PDF.
    counters = defaultdict(int)

    total = 0
    failed = 0

    try:
        # Postupné zpracování všech stránek PDF
        for page_index in range(len(document)):

            page_number = page_index + 1

            print(f"\nZpracovávám stránku {page_number}/{len(document)}...")

            matrix = pymupdf.Matrix(DPI / 72, DPI / 72)
            pix = document[page_index].get_pixmap(
                matrix=matrix,
                alpha=False
            )

            rgb = np.frombuffer(
                pix.samples,
                dtype=np.uint8
            ).reshape(pix.height, pix.width, 3)

            # Najdi tabulku a narovnej ji
            try:
                grid = find_grid_and_warp(rgb)
            except RuntimeError as error:
                print(f"Chyba na stránce {page_number}: {error}")
                continue

            cell_width = grid.shape[1] / COLS
            cell_height = grid.shape[0] / ROWS

            # Procházení všech 100 buněk na stránce
            for row in range(ROWS):
                for col in range(COLS):

                    # Sloupec určuje číslici 0-9
                    digit_value = col

                    x1 = int(
                        col * cell_width +
                        cell_width * CELL_INSET
                    )
                    x2 = int(
                        (col + 1) * cell_width -
                        cell_width * CELL_INSET
                    )

                    y1 = int(
                        row * cell_height +
                        cell_height * CELL_INSET
                    )
                    y2 = int(
                        (row + 1) * cell_height -
                        cell_height * CELL_INSET
                    )

                    cell = grid[y1:y2, x1:x2]

                    digit_image = prepare_digit(cell)

                    # Číslování pokračuje i na další stránce
                    counters[digit_value] += 1
                    sample_number = counters[digit_value]

                    filename = f"{digit_value}_{sample_number}.png"

                    output_path = os.path.join(
                        OUTPUT_DIR,
                        filename
                    )

                    if digit_image is None:
                        failed += 1
                        digit_image = np.full(
                            (OUTPUT_SIZE, OUTPUT_SIZE),
                            255,
                            dtype=np.uint8
                        )

                    cv2.imwrite(output_path, digit_image)

                    total += 1

            print(f"Stránka {page_number} dokončena.")

    finally:
        document.close()

    print("\n========== HOTOVO ==========")
    print(f"Zpracováno stran: {len(document)}")
    print(f"Vytvořeno obrázků: {total}")
    print(f"Prázdné obrázky: {failed}")
    print(f"Uloženo do: {OUTPUT_DIR}")
    print("============================")

if __name__ == "__main__":
    process_pdf()