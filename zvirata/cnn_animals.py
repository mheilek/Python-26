
import os
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageFile
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


# ==========================================
# KONFIGURACE
# ==========================================

IMAGE_SIZE = 256

CLASS_NAMES = [
    "elephant",
    "dog",
    "cat",
    "fish",
    "parrot"
]

OUTPUT_SIZE = len(CLASS_NAMES)

TRAIN_PATH = "test_set_animals"

VALIDATION_PATH = "animals"

MODEL_PATH = "model_animals_new.pth"

LEARNING_RATE = 0.001
BATCH_SIZE = 16
EPOCHS = 5

WEIGHT_DECAY = 0.0001
EARLY_STOPPING_PATIENCE = 10

VALIDATION_RATIO = 0.20

SEED = 42

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"Používané zařízení: {DEVICE}")

ImageFile.LOAD_TRUNCATED_IMAGES = True


# ==========================================
# RANDOM SEED
# ==========================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


# ==========================================
# DATA AUGMENTATION
# ==========================================

train_transform = transforms.Compose([

    transforms.RandomHorizontalFlip(p=0.5),

    transforms.RandomAffine(
        degrees=10,
        translate=(0.05, 0.05),
        scale=(0.90, 1.10),
        shear=3,
        fill=1.0
    ),

    transforms.ColorJitter(
        brightness=0.15,
        contrast=0.15,
        saturation=0.15
    )

    

])


# ==========================================
# CNN BLOCK
# ==========================================

class ConvBlock(nn.Module):

    def __init__(self, in_channels, out_channels):

        super().__init__()

        self.block = nn.Sequential(

            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=5,
                padding=1
            ),

            nn.ReLU(inplace=True),

            nn.MaxPool2d(2)

        )

    def forward(self, x):

        return self.block(x)


# ==========================================
# CNN MODEL
# ==========================================

class NeuralNetwork(nn.Module):

    def __init__(self):

        super().__init__()

        self.conv_layers = nn.Sequential(

            ConvBlock(3, 16),
            ConvBlock(16, 32),
            ConvBlock(32, 64),
            ConvBlock(64, 128)

        )

        self.classifier = nn.Sequential(

            nn.AdaptiveAvgPool2d((1, 1)),

            nn.Flatten(),

            nn.Linear(128, 256),

            nn.ReLU(inplace=True),

            nn.Dropout(0.15),

            nn.Linear(256, OUTPUT_SIZE)

        )

    def forward(self, x):

        x = self.conv_layers(x)

        return self.classifier(x)


# ==========================================
# NAČÍTÁNÍ OBRÁZKŮ
# ==========================================

def load_image(path):

    with Image.open(path) as img:

        img = img.convert("RGB")

        img = img.resize(
            (IMAGE_SIZE, IMAGE_SIZE),
            Image.Resampling.LANCZOS
        )

        pixels = np.array(
            img,
            dtype=np.float32
        )

    X = torch.from_numpy(pixels)

    X = X.permute(2, 0, 1)

    X.div_(255.0)

    return X


# ==========================================
# NAČTENÍ DATASETU
# ==========================================

def load_all_data(dataset_path):

    data = []

    extensions = [
        "*.jpg",
        "*.jpeg",
        "*.png",
        "*.bmp",
        "*.webp"
    ]

    print(f"\nNačítám dataset: {dataset_path}\n")

    for label, class_name in enumerate(CLASS_NAMES):

        folder = Path(dataset_path) / class_name

        if not folder.exists():

            raise RuntimeError(
                f"CHYBÍ SLOŽKA: {folder}"
            )

        class_paths = list({
        path.resolve()
        for path in folder.iterdir()
        if path.is_file()
        and path.suffix.lower() in [
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    ]
})

        valid_paths = []

        for path in class_paths:

            try:

                with Image.open(path) as img:
                    img.verify()

                valid_paths.append(str(path))

            except Exception:

                print(f"Neplatný obrázek: {path}")

        for path in valid_paths:

            data.append((path, label))

        print(
            f"{class_name}: {len(valid_paths)} obrázků"
        )

        if len(valid_paths) == 0:

            raise RuntimeError(
                f"Třída {class_name} neobsahuje obrázky!"
            )

    return data


# ==========================================
# ROZDĚLENÍ DATASETU
# ==========================================




# ==========================================
# DATASET CLASS
# ==========================================

class AnimalDataset(Dataset):

    def __init__(self, data, transform=None):

        self.data = data
        self.transform = transform

    def __len__(self):

        return len(self.data)

    def __getitem__(self, index):

        path, label = self.data[index]

        X = load_image(path)

        if self.transform is not None:

            X = self.transform(X)

        Y = torch.tensor(
            label,
            dtype=torch.long
        )

        return X, Y

# ==========================================
# NAČTENÍ MODELU
# ==========================================

def load_model():

    model = NeuralNetwork().to(DEVICE)

    if not os.path.exists(MODEL_PATH):

        print("Vytvářím nový model!")

        return model, None

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=True
    )

    if checkpoint.get("class_names") != CLASS_NAMES:

        print("Nekompatibilní třídy v checkpointu!")

        print("Vytvářím nový model.")

        return model, None

    try:

        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        print("Předchozí model byl načten!")

        return model, checkpoint

    except RuntimeError:

        print("Nekompatibilní checkpoint!")

        return model, None


# ==========================================
# ULOŽENÍ CHECKPOINTU
# ==========================================

def save_model(
    model,
    optimizer,
    epoch,
    best_loss
):

    torch.save({

        "model_state_dict": model.state_dict(),

        "optimizer_state_dict": optimizer.state_dict(),

        "epoch": epoch,

        "best_loss": best_loss,

        "class_names": CLASS_NAMES

    }, MODEL_PATH)

    print("Checkpoint uložen!")


# ==========================================
# TRAINING
# ==========================================

def train_epoch(
    model,
    loader,
    optimizer,
    criterion,
    epoch
):

    model.train()

    total_loss = 0.0

    correct = 0
    incorrect = 0
    total = 0

    progress = tqdm(
        loader,
        desc=f"Training {epoch}",
        unit="batch"
    )

    for X, Y in progress:

        X = X.to(DEVICE)
        Y = Y.to(DEVICE)

        optimizer.zero_grad(set_to_none=True)

        output = model(X)

        loss = criterion(output, Y)

        loss.backward()

        optimizer.step()

        predictions = output.argmax(dim=1)

        correct += (predictions == Y).sum().item()

        incorrect += (predictions != Y).sum().item()

        total += Y.size(0)

        total_loss += loss.item() * X.size(0)

        progress.set_postfix(

            loss=f"{loss.item():.5f}",

            accuracy=f"{correct / total * 100:.2f}%"

        )

    average_loss = total_loss / total

    accuracy = correct / total * 100

    return average_loss, accuracy, correct, incorrect


# ==========================================
# VALIDATION
# ==========================================

def validate(
    model,
    loader,
    criterion,
    description="VALIDATION"
):

    model.eval()

    total_loss = 0.0

    correct = 0
    incorrect = 0
    total = 0

    class_correct = [0] * OUTPUT_SIZE

    class_total = [0] * OUTPUT_SIZE

    confusion_matrix = torch.zeros(
        OUTPUT_SIZE,
        OUTPUT_SIZE,
        dtype=torch.int64
    )

    print("\n--- VALIDACE ---\n")

    with torch.inference_mode():

        for X, Y in loader:

            X = X.to(DEVICE)
            Y = Y.to(DEVICE)

            output = model(X)

            loss = criterion(output, Y)

            predictions = output.argmax(dim=1)

            for actual, prediction in zip(
                Y.cpu(),
                predictions.cpu()
            ):

                confusion_matrix[
                    actual.item(),
                    prediction.item()
                ] += 1

            total_loss += loss.item() * X.size(0)

            for actual, prediction in zip(
                Y.cpu(),
                predictions.cpu()
            ):

                actual = actual.item()

                prediction = prediction.item()

                total += 1

                class_total[actual] += 1

                if prediction == actual:

                    correct += 1

                    class_correct[actual] += 1

                    status = "OK"

                else:

                    incorrect += 1

                    status = "CHYBA"

                accuracy = correct / total * 100

                tqdm.write(

                    f"[{status}] "

                    f"Skutečnost: {CLASS_NAMES[actual]} | "

                    f"Rozpoznáno: {CLASS_NAMES[prediction]} | "

                    f"Accuracy: {accuracy:.2f}%"

                )

    if total == 0:

        raise RuntimeError(
            "Validační dataset je prázdný!"
        )

    average_loss = total_loss / total

    accuracy = correct / total * 100

    print("\n--------------------------------")

    print(f"{description} Loss: {average_loss:.6f}")

    print(f"Správně: {correct}")

    print(f"Špatně: {incorrect}")

    print(f"Úspěšnost: {accuracy:.2f}%")

    print("--------------------------------")

    # CONFUSION MATRIX

    print("\nMATICE ZÁMĚN")

    print("Řádky = skutečnost, sloupce = predikce\n")

    print(
        " " * 12 +
        " ".join(f"{name[:8]:>9}" for name in CLASS_NAMES)
    )

    for i, name in enumerate(CLASS_NAMES):

        print(

            f"{name:<12}" +

            " ".join(
                f"{int(x):9d}"
                for x in confusion_matrix[i]
            )

        )

    return (
        average_loss,
        accuracy,
        correct,
        incorrect,
        class_correct,
        class_total
    )

# ==========================================
# TRÉNOVÁNÍ
# ==========================================

def train():

    training_data = load_all_data(TRAIN_PATH)

    training_dataset = AnimalDataset(
        training_data,
        transform=train_transform
    )

    training_loader = DataLoader(
        training_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=(DEVICE.type == "cuda")
    )

    model, checkpoint = load_model()

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )

    start_epoch = 0
    best_loss = float("inf")

    # POKRAČOVÁNÍ V TRÉNOVÁNÍ
    if checkpoint is not None:

        if "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(
                checkpoint["optimizer_state_dict"]
            )

        for param_group in optimizer.param_groups:
            param_group["lr"] = LEARNING_RATE

        start_epoch = checkpoint.get("epoch", 0)
        best_loss = checkpoint.get("best_loss", float("inf"))

        print(f"Pokračuji od epochy {start_epoch + 1}")

    # TRÉNOVÁNÍ
    for epoch in range(start_epoch, start_epoch + EPOCHS):

        print("\\n========================================")
        print(f"EPOCH: {epoch + 1}")
        print("========================================")

        train_loss, train_accuracy, train_correct, train_incorrect = train_epoch(
            model,
            training_loader,
            optimizer,
            criterion,
            epoch + 1
        )

        print("\\n--- TRAINING VÝSLEDKY ---")
        print(f"Train Loss: {train_loss:.6f}")
        print(f"Správně: {train_correct}")
        print(f"Špatně: {train_incorrect}")
        print(f"Train Accuracy: {train_accuracy:.2f}%")

        # ULOŽENÍ MODELU PO KAŽDÉ EPOCHĚ
        save_model(
            model,
            optimizer,
            epoch + 1,
            best_loss
        )

    print("\\n========================================")
    print("TRÉNOVÁNÍ DOKONČENO")
    print(f"Poslední dokončená epocha: {start_epoch + EPOCHS}")
    print("Evaluace nebyla spuštěna.")
    print("========================================")


# ==========================================
# SAMOSTATNÁ VALIDACE
# ==========================================

def evaluate_model():

    if not os.path.exists(MODEL_PATH):

        print("Model nebyl nalezen!")

        return

    validation_data = load_all_data(VALIDATION_PATH)

    model = NeuralNetwork().to(DEVICE)

    checkpoint = torch.load(

        MODEL_PATH,

        map_location=DEVICE,

        weights_only=True

    )

    if checkpoint.get("class_names") != CLASS_NAMES:

        print("Checkpoint má jiné třídy!")

        return

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    dataset = AnimalDataset(
        validation_data,
        transform=None
    )

    loader = DataLoader(

        dataset,

        batch_size=BATCH_SIZE,

        shuffle=False

    )

    criterion = nn.CrossEntropyLoss()

    (
        loss,
        accuracy,
        correct,
        incorrect,
        class_correct,
        class_total
    ) = validate(

        model,

        loader,

        criterion,

        description="VALIDATION"

    )

    print("\n========================================")

    print("          CELKOVÉ VÝSLEDKY")

    print("========================================")

    print(f"Počet obrázků: {correct + incorrect}")

    print(f"Správně: {correct}")

    print(f"Špatně: {incorrect}")

    print(f"Average Loss: {loss:.6f}")

    print("----------------------------------------")

    print(f"CELKOVÁ ÚSPĚŠNOST: {accuracy:.2f}%")

    print("----------------------------------------")

    for label, name in enumerate(CLASS_NAMES):

        if class_total[label] > 0:

            class_accuracy = (

                class_correct[label] /

                class_total[label] * 100

            )

            print(

                f"{name}: "

                f"{class_accuracy:.2f}% "

                f"({class_correct[label]}/"

                f"{class_total[label]})"

            )

    print("========================================")


# ==========================================
# HLAVNÍ PROGRAM
# ==========================================

if __name__ == "__main__":

    # "train" = pouze trénování (bez evaluace)
    # "evaluate" = samostatná evaluace uloženého modelu

    MODE = "train"

    if MODE == "train":
        train()

    elif MODE == "evaluate":
        evaluate_model()

    else:
        print("Neznámý režim! Použij 'train' nebo 'evaluate'.")