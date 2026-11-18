
import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import Dataset, DataLoader, random_split

from PIL import Image
from tqdm import tqdm

import numpy as np
import glob
import os
import random


# ==========================================
# KONFIGURACE
# ==========================================

IMAGE_SIZE = 256

OUTPUT_SIZE = 10

LEARNING_RATE = 0.0003

BATCH_SIZE = 8

EPOCHS = 20

WEIGHT_DECAY = 0.0001

EARLY_STOPPING_PATIENCE = 5

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"Používané zařízení: {DEVICE}")


# ==========================================
# CNN MODEL
# ==========================================

class NeuralNetwork(nn.Module):

    def __init__(self):

        super().__init__()

        self.conv_layers = nn.Sequential(

            nn.Conv2d(
                1, 32,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(2),

            nn.Conv2d(
                32, 64,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(2),

            nn.Conv2d(
                64, 128,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(2)

        )

        self.classifier = nn.Sequential(

            nn.AdaptiveAvgPool2d((1, 1)),

            nn.Flatten(),

            nn.Linear(128, 256),

            nn.ReLU(),

            nn.Dropout(0.3),

            nn.Linear(256, OUTPUT_SIZE)

        )

    def forward(self, X):

        X = self.conv_layers(X)

        X = self.classifier(X)

        return X


# ==========================================
# NAČÍTÁNÍ OBRÁZKŮ
# ==========================================

def load_image(path):

    with Image.open(path) as img:

        img = img.convert("L")

        img = img.resize(
            (IMAGE_SIZE, IMAGE_SIZE)
        )

        pixels = np.array(
            img,
            dtype=np.float32
        )

    X = torch.from_numpy(pixels)

    X = X.unsqueeze(0)

    X.div_(255.0)

    return X


# ==========================================
# NAČÍTÁNÍ TRÉNOVACÍCH DAT
# ==========================================

def load_training_data():

    training_data = []

    paths = glob.glob(
        "vycentrovane_train/*.png"
    )

    for path in paths:

        filename = os.path.basename(path)

        try:

            label = int(
                filename.split("_")[0]
            )

        except ValueError:

            print(f"Přeskakuji soubor: {filename}")

            continue

        if label < 0 or label >= OUTPUT_SIZE:

            print(f"Neplatný label: {filename}")

            continue

        training_data.append(
            (path, label)
        )

    print(
        f"Nalezeno obrázků: {len(training_data)}"
    )

    return training_data


# ==========================================
# DATASET
# ==========================================

class NumberDataset(Dataset):

    def __init__(self, data):

        self.data = data

    def __len__(self):

        return len(self.data)

    def __getitem__(self, index):

        path, label = self.data[index]

        X = load_image(path)

        Y = torch.tensor(
            label,
            dtype=torch.long
        )

        return X, Y


# ==========================================
# UKLÁDÁNÍ CHECKPOINTU
# ==========================================

def save_model(
    model,
    optimizer,
    scheduler,
    epoch,
    best_loss
):

    torch.save({

        "model_state_dict": model.state_dict(),

        "optimizer_state_dict": optimizer.state_dict(),

        "scheduler_state_dict": scheduler.state_dict(),

        "epoch": epoch,

        "best_loss": best_loss

    }, "model.pth")

    print("Nejlepší checkpoint uložen!")


# ==========================================
# NAČÍTÁNÍ MODELU
# ==========================================

def load_model():

    model = NeuralNetwork().to(DEVICE)

    if not os.path.exists("model.pth"):

        print("Vytvářím nový model!")

        return model, None

    checkpoint = torch.load(
        "model.pth",
        map_location=DEVICE,
        weights_only=True
    )

    if "model_state_dict" in checkpoint:

        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        print("Předchozí model byl načten!")

        return model, checkpoint

    else:

        model.load_state_dict(checkpoint)

        print("Načten starý formát modelu.")

        return model, None


# ==========================================
# TRÉNOVÁNÍ
# ==========================================

def train(
    training_loader,
    validation_loader,
    model,
    optimizer,
    scheduler,
    epochs,
    start_epoch=0,
    best_loss=float("inf")
):

    criterion = nn.CrossEntropyLoss()

    epochs_without_improvement = 0

    for epoch in range(
        start_epoch,
        start_epoch + epochs
    ):

        # ==================================
        # TRAINING
        # ==================================

        model.train()

        train_loss = 0.0

        train_correct = 0

        train_total = 0

        progress = tqdm(
            training_loader,
            desc=f"Training {epoch + 1}",
            unit="batch"
        )

        for X, Y in progress:

            X = X.to(DEVICE)

            Y = Y.to(DEVICE)

            optimizer.zero_grad(
                set_to_none=True
            )

            output = model(X)

            loss = criterion(output, Y)

            loss.backward()

            optimizer.step()

            train_loss += (
                loss.item() * X.size(0)
            )

            predictions = output.argmax(dim=1)

            train_correct += (
                predictions == Y
            ).sum().item()

            train_total += Y.size(0)

            progress.set_postfix(
                loss=f"{loss.item():.5f}"
            )

        if train_total == 0:

            print("Prázdný trénovací dataset!")

            return model

        train_loss /= train_total

        train_accuracy = (
            train_correct / train_total * 100
        )

        # ==================================
        # VALIDATION
        # ==================================

        model.eval()

        validation_loss = 0.0

        validation_correct = 0

        validation_total = 0

        with torch.inference_mode():

            for X, Y in validation_loader:

                X = X.to(DEVICE)

                Y = Y.to(DEVICE)

                output = model(X)

                loss = criterion(output, Y)

                validation_loss += (
                    loss.item() * X.size(0)
                )

                predictions = output.argmax(dim=1)

                validation_correct += (
                    predictions == Y
                ).sum().item()

                validation_total += Y.size(0)

        if validation_total == 0:

            print("Prázdný validační dataset!")

            return model

        validation_loss /= validation_total

        validation_accuracy = (
            validation_correct /
            validation_total * 100
        )

        # ==================================
        # SCHEDULER
        # ==================================

        scheduler.step(validation_loss)

        current_lr = optimizer.param_groups[0]["lr"]

        # ==================================
        # VÝPIS VÝSLEDKŮ
        # ==================================

        print("\n================================")

        print(f"EPOCH: {epoch + 1}")

        print(f"Train Loss: {train_loss:.6f}")

        print(f"Train Accuracy: {train_accuracy:.2f}%")

        print(
            f"Validation Loss: {validation_loss:.6f}"
        )

        print(
            f"Validation Accuracy: "
            f"{validation_accuracy:.2f}%"
        )

        print(f"Learning Rate: {current_lr:.8f}")

        print("================================")

        # ==================================
        # UKLÁDÁNÍ NEJLEPŠÍHO MODELU
        # ==================================

        if validation_loss < best_loss:

            best_loss = validation_loss

            epochs_without_improvement = 0

            save_model(
                model,
                optimizer,
                scheduler,
                epoch + 1,
                best_loss
            )

            print("Nový nejlepší model!")

        else:

            epochs_without_improvement += 1

            print(
                f"Bez zlepšení: "
                f"{epochs_without_improvement}/"
                f"{EARLY_STOPPING_PATIENCE}"
            )

        # ==================================
        # EARLY STOPPING
        # ==================================

        if (
            epochs_without_improvement
            >= EARLY_STOPPING_PATIENCE
        ):

            print("\nEarly stopping aktivován!")

            break

    return model


# ==========================================
# TRÉNOVÁNÍ CHECKPOINTU
# ==========================================

def train_checkpoint():

    training_data = load_training_data()

    if len(training_data) < 2:

        print("Nedostatek trénovacích obrázků!")

        return

    dataset = NumberDataset(training_data)

    # ==================================
    # ROZDĚLENÍ DAT
    # ==================================

    validation_size = max(
        1,
        int(len(dataset) * 0.2)
    )

    training_size = (
        len(dataset) - validation_size
    )

    training_dataset, validation_dataset = random_split(

        dataset,

        [training_size, validation_size],

        generator=torch.Generator().manual_seed(42)

    )

    print(
        f"Trénovací obrázky: {training_size}"
    )

    print(
        f"Validační obrázky: {validation_size}"
    )

    # ==================================
    # DATALOADERS
    # ==================================

    training_loader = DataLoader(

        training_dataset,

        batch_size=BATCH_SIZE,

        shuffle=True,

        num_workers=0

    )

    validation_loader = DataLoader(

        validation_dataset,

        batch_size=BATCH_SIZE,

        shuffle=False,

        num_workers=0

    )

    # ==================================
    # MODEL
    # ==================================

    model, checkpoint = load_model()

    optimizer = optim.Adam(

        model.parameters(),

        lr=LEARNING_RATE,

        weight_decay=WEIGHT_DECAY

    )

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(

        optimizer,

        mode="min",

        factor=0.5,

        patience=2,

        min_lr=0.00001

    )

    start_epoch = 0

    best_loss = float("inf")

    # ==================================
    # OBNOVENÍ CHECKPOINTU
    # ==================================

    if checkpoint is not None:

        optimizer.load_state_dict(
            checkpoint["optimizer_state_dict"]
        )

        start_epoch = checkpoint.get(
            "epoch",
            0
        )

        best_loss = checkpoint.get(
            "best_loss",
            float("inf")
        )

        if "scheduler_state_dict" in checkpoint:

            scheduler.load_state_dict(
                checkpoint["scheduler_state_dict"]
            )

        print(
            f"Pokračuji od epochy {start_epoch + 1}"
        )

    # ==================================
    # START TRAINING
    # ==================================

    train(

        training_loader=training_loader,

        validation_loader=validation_loader,

        model=model,

        optimizer=optimizer,

        scheduler=scheduler,

        epochs=EPOCHS,

        start_epoch=start_epoch,

        best_loss=best_loss

    )

    print("\n--- TRÉNOVÁNÍ DOKONČENO ---")


# ==========================================
# VYHODNOCENÍ MODELU
# ==========================================

def evaluate_model():

    model, checkpoint = load_model()

    paths = glob.glob(
        "eval_data/cislice/*/*.png"
    )

    if not paths:

        print("Nebyly nalezeny testovací obrázky!")

        return

    criterion = nn.CrossEntropyLoss()

    correct = 0

    incorrect = 0

    total_loss = 0.0

    model.eval()

    print("\n--- TESTOVÁNÍ NEURONOVÉ SÍTĚ ---\n")

    with torch.inference_mode():

        progress = tqdm(
            paths,
            desc="Testing",
            unit="image"
        )

        for path in progress:

            filename = os.path.basename(path)

            try:

                actual_label = int(
                    filename.split("_")[0]
                )

            except ValueError:

                continue

            if not 0 <= actual_label < OUTPUT_SIZE:

                continue

            X = load_image(path).unsqueeze(0).to(DEVICE)

            Y = torch.tensor(
                [actual_label],
                dtype=torch.long,
                device=DEVICE
            )

            output = model(X)

            loss = criterion(output, Y)

            total_loss += loss.item()

            prediction = output.argmax(dim=1).item()

            if prediction == actual_label:

                correct += 1

            else:

                incorrect += 1

                tqdm.write(
                    f"CHYBA: {filename} | "
                    f"Správně: {actual_label} | "
                    f"Rozpoznáno: {prediction}"
                )

            total = correct + incorrect

            progress.set_postfix(
                accuracy=f"{correct / total * 100:.2f}%"
            )

    total = correct + incorrect

    if total == 0:

        print("Žádné platné testovací obrázky!")

        return

    accuracy = correct / total * 100

    average_loss = total_loss / total

    print("\n================================")

    print("       VÝSLEDKY TESTOVÁNÍ")

    print("================================")

    print(f"Testovací obrázky: {total}")

    print(f"Správně: {correct}")

    print(f"Špatně: {incorrect}")

    print(f"Average Loss: {average_loss:.6f}")

    print("--------------------------------")

    print(f"ACCURACY: {accuracy:.2f}%")

    print("================================")


# ==========================================
# PREDIKCE OBRÁZKU
# ==========================================

def predict_image(path):

    model, checkpoint = load_model()

    X = load_image(path).unsqueeze(0).to(DEVICE)

    model.eval()

    with torch.inference_mode():

        output = model(X)

        probabilities = torch.softmax(
            output,
            dim=1
        )

    results = probabilities[0].cpu().tolist()

    prediction = results.index(max(results))

    confidence = max(results) * 100

    print(f"Rozpoznané číslo: {prediction}")

    print(f"Jistota sítě: {confidence:.2f}%")

    return prediction


# ==========================================
# HLAVNÍ PROGRAM
# ==========================================

if __name__ == "__main__":

    # True = trénování
    # False = testování

    TRAIN_MODE = False

    if TRAIN_MODE:

        train_checkpoint()

    else:

        evaluate_model()
