import torch
import torch.nn as nn
import torch.optim as optim

from PIL import Image
from tqdm import tqdm

import glob
import random
import os


# ==========================================
# KONFIGURACE
# ==========================================

IMAGE_SIZE = 256

OUTPUT_SIZE = 10

LEARNING_RATE = 0.001

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"Používané zařízení: {DEVICE}")


# ==========================================
# KONVOLUČNÍ NEURONOVÁ SÍŤ (CNN)
# ==========================================

class NeuralNetwork(nn.Module):

    def __init__(self):

        super().__init__()

        # Konvoluční vrstvy
        self.conv_layers = nn.Sequential(

            # 1 -> 32 filtrů
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(2),

            # 32 -> 64 filtrů
            nn.Conv2d(
                in_channels=32,
                out_channels=64,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(2),

            # 64 -> 128 filtrů
            nn.Conv2d(
                in_channels=64,
                out_channels=128,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(2)

        )

        # Klasifikační vrstvy
        self.classifier = nn.Sequential(

            nn.AdaptiveAvgPool2d((1, 1)),

            nn.Flatten(),

            nn.Linear(128, 128),

            nn.ReLU(),

            nn.Dropout(0.3),

            nn.Linear(128, OUTPUT_SIZE)

        )

    def forward(self, X):

        X = self.conv_layers(X)

        X = self.classifier(X)

        return X


# ==========================================
# NAČÍTÁNÍ OBRÁZKŮ
# ==========================================

def load_image(path):

    img = Image.open(path).convert("L")

    img = img.resize((IMAGE_SIZE, IMAGE_SIZE))

    pixels = list(img.getdata())

    # Normalizace pixelů 0-1
    pixels = [pixel / 255.0 for pixel in pixels]

    X = torch.tensor(
        pixels,
        dtype=torch.float32
    )

    # Rozměr: 1 x 256 x 256
    X = X.reshape(1, IMAGE_SIZE, IMAGE_SIZE)

    return X


# ==========================================
# NAČÍTÁNÍ TRÉNOVACÍCH DAT
# ==========================================

def load_training_data():

    training_data = []

    paths = glob.glob("vycentrovane_train/*.png")

    for path in paths:

        filename = os.path.basename(path)

        # Label je číslo před podtržítkem
        label = int(filename.split("_")[0])

        if label < 0 or label >= OUTPUT_SIZE:
            print(f"Přeskakuji neplatný label: {filename}")
            continue

        training_data.append((path, label))

    print(f"Nalezeno obrázků: {len(training_data)}")

    return training_data


# ==========================================
# TRÉNOVÁNÍ
# ==========================================


def train(training_data, epochs, learning_rate, model, optimizer=None, start_epoch=0):

    criterion = nn.CrossEntropyLoss()

    if optimizer is None:

        optimizer = optim.Adam(
            model.parameters(),
            lr=learning_rate
        )

    model.train()

    for epoch in range(start_epoch, start_epoch + epochs):

        print(f"\nEpoch {epoch + 1}")

        random.shuffle(training_data)

        total_loss = 0

        progress_bar = tqdm(
            training_data,
            desc=f"Training {epoch + 1}",
            unit="image"
        )

        for path, label in progress_bar:

            X = load_image(path).unsqueeze(0).to(DEVICE)

            Y = torch.tensor(
                [label],
                dtype=torch.long,
                device=DEVICE
            )

            optimizer.zero_grad()

            output = model(X)

            loss = criterion(output, Y)

            loss.backward()

            optimizer.step()

            current_loss = loss.item()

            total_loss += current_loss

            progress_bar.set_postfix(
                loss=f"{current_loss:.6f}",
                avg_loss=f"{total_loss / (progress_bar.n + 1):.6f}",
                image=os.path.basename(path)
            )

        average_loss = total_loss / len(training_data)

        print(
            f"\nEpoch {epoch + 1}, "
            f"Average Loss: {average_loss:.6f}"
        )

        # Uložení po každé epoše
        save_model(model, optimizer, epoch + 1)

    return model
# ==========================================
# UKLÁDÁNÍ MODELU
# ==========================================

def save_model(model, optimizer, epoch):

    torch.save({
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "epoch": epoch
    }, "model.pth")

    print("Checkpoint uložen!")

# ==========================================
# NAČÍTÁNÍ MODELU
# ==========================================


def load_model():

    model = NeuralNetwork().to(DEVICE)

    if os.path.exists("model.pth"):

        checkpoint = torch.load(
            "model.pth",
            map_location=DEVICE,
            weights_only=True
        )

        # Kontrola, zda jde o nový formát checkpointu
        if "model_state_dict" in checkpoint:

            model.load_state_dict(
                checkpoint["model_state_dict"]
            )

            print("Předchozí model byl načten!")

            return model, checkpoint

        else:

            # Starý formát obsahující pouze váhy
            model.load_state_dict(checkpoint)

            print("Načten starý formát modelu.")
            print("Optimalizátor a epocha budou inicializovány od začátku.")

            return model, None

    else:

        print("Vytvářím nový model!")

        return model, None



# ==========================================
# PREDIKCE OBRÁZKU
# ==========================================

def predict_image(path):

    model = load_model()

    X = load_image(path).unsqueeze(0).to(DEVICE)

    model.eval()

    with torch.no_grad():

        output = model(X)

        probabilities = torch.softmax(output, dim=1)

    results = probabilities[0].cpu().tolist()

    prediction = results.index(max(results))

    print(f"Rozpoznané číslo: {prediction}")

    print(
        f"Jistota sítě: {max(results) * 100:.2f} %"
    )

    return prediction


# ==========================================
# VYHODNOCENÍ MODELU
# ==========================================

# ==========================================
# VYHODNOCENÍ MODELU
# ==========================================

def evaluate_model():

    model, checkpoint = load_model()

    paths = glob.glob("vycentrovane_validation/*.png")

    if len(paths) == 0:
        print("Ve složce vycentrovane_test nebyly nalezeny žádné obrázky!")
        return

    correct = 0
    incorrect = 0

    total_loss = 0

    criterion = nn.CrossEntropyLoss()

    print("\n--- TESTOVÁNÍ NEURONOVÉ SÍTĚ ---\n")

    model.eval()

    with torch.no_grad():

        progress_bar = tqdm(
            paths,
            desc="Testing",
            unit="image"
        )

        for path in progress_bar:

            filename = os.path.basename(path)

            # Správná číslice z názvu souboru
            actual_label = int(filename.split("_")[0])

            if actual_label < 0 or actual_label >= OUTPUT_SIZE:
                continue

            # Načtení obrázku
            X = load_image(path).unsqueeze(0).to(DEVICE)

            Y = torch.tensor(
                [actual_label],
                dtype=torch.long,
                device=DEVICE
            )

            # FORWARD
            output = model(X)

            # Loss
            loss = criterion(output, Y)

            total_loss += loss.item()

            # Predikce
            prediction = torch.argmax(
                output,
                dim=1
            ).item()

            if prediction == actual_label:

                correct += 1

            else:

                incorrect += 1

                tqdm.write(
                    f"CHYBA: {filename} | "
                    f"Správně: {actual_label} | "
                    f"Rozpoznáno: {prediction}"
                )

            progress_bar.set_postfix(
                accuracy=f"{correct / (correct + incorrect) * 100:.2f}%"
            )

    total = correct + incorrect

    if total == 0:
        print("Nebyly nalezeny žádné platné testovací obrázky!")
        return

    accuracy = (correct / total) * 100

    average_loss = total_loss / total

    print("\n================================")
    print("       VÝSLEDKY TESTOVÁNÍ")
    print("================================")

    print(f"Počet testovacích obrázků: {total}")

    print(f"Správně rozpoznáno: {correct}")

    print(f"Špatně rozpoznáno: {incorrect}")

    print(f"Průměrný Loss: {average_loss:.6f}")

    print("--------------------------------")

    print(f"ÚSPĚŠNOST NEURONOVÉ SÍTĚ: {accuracy:.2f} %")

    print("================================")

# ==========================================
# HLAVNÍ PROGRAM - TRÉNOVÁNÍ
# ==========================================

if __name__ == "__main__":

  #  training_data = load_training_data()
#
  #  if len(training_data) == 0:
  #      print("Nebyly nalezeny žádné trénovací obrázky!")
  #      exit()
#
  #  model, checkpoint = load_model()
#
  #  optimizer = optim.Adam(
  #      model.parameters(),
  #      lr=LEARNING_RATE
  #  )
#
  #  start_epoch = 0
#
  #  if checkpoint is not None:
#
  #      optimizer.load_state_dict(
  #          checkpoint["optimizer_state_dict"]
  #      )
#
  #      start_epoch = checkpoint["epoch"]
#
  #      print(f"Pokračuji od epochy {start_epoch + 1}")
#
  #  model = train(
  #      training_data=training_data,
  #      epochs=5,
  #      learning_rate=LEARNING_RATE,
  #      model=model,
  #      optimizer=optimizer,
  #      start_epoch=start_epoch
  #  )
#
  #  print("\n--- TRÉNOVÁNÍ DOKONČENO ---")

    # Automatické vyhodnocení
    evaluate_model()