
import os
import glob
import random
import numpy as np

from PIL import Image
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
OUTPUT_SIZE = 10

LEARNING_RATE = 0.001
BATCH_SIZE = 8
EPOCHS = 60

WEIGHT_DECAY = 0.0001
EARLY_STOPPING_PATIENCE = 10

SEED = 42

MODEL_PATH = "model.pth"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"Používané zařízení: {DEVICE}")


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

    transforms.RandomAffine(
        degrees=3,
        translate=(0.03, 0.03),
        scale=(0.98, 1.02),
        shear=1,
        fill=1.0
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

            ConvBlock(1, 16),
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

        x = self.classifier(x)

        return x


# ==========================================
# NAČÍTÁNÍ OBRÁZKŮ
# ==========================================

def load_image(path):

    with Image.open(path) as img:

        img = img.convert("L")

        img = img.resize(
            (IMAGE_SIZE, IMAGE_SIZE),
            Image.Resampling.LANCZOS
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

    data = []

    paths = glob.glob(
        "vycentrovane_train/*.png"
    )

    for path in paths:

        filename = os.path.basename(path)

        try:
            label = int(filename.split("_")[0])
        except ValueError:
            print(f"Přeskakuji: {filename}")
            continue

        if 0 <= label < OUTPUT_SIZE:
            data.append((path, label))

    print(f"Trénovacích obrázků: {len(data)}")

    return data


# ==========================================
# NAČÍTÁNÍ VALIDAČNÍCH DAT
# ==========================================

def load_validation_data():

    data = []

    paths = glob.glob(
        "eval_data/cislice/*/*.png"
    )

    for path in paths:

        filename = os.path.basename(path)

        try:
            label = int(filename.split("_")[0])
        except ValueError:
            print(f"Přeskakuji: {filename}")
            continue

        if 0 <= label < OUTPUT_SIZE:
            data.append((path, label))

    print(f"Validačních obrázků: {len(data)}")

    return data


# ==========================================
# DATASET
# ==========================================

class NumberDataset(Dataset):

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
# ULOŽENÍ CHECKPOINTU
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

    }, MODEL_PATH)

    print("Nejlepší checkpoint uložen!")


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

    if "model_state_dict" not in checkpoint:

        print("Neplatný checkpoint. Vytvářím nový model!")

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
        

        for i in range(len(Y)):

            actual = Y[i].item()

            prediction = predictions[i].item()

            total += 1

            if prediction == actual:

                correct += 1
                status = "OK"

            else:

                incorrect += 1
                status = "CHYBA"


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

            for actual, prediction in zip(Y.cpu(), predictions.cpu()):
                confusion_matrix[actual, prediction] += 1

            total_loss += loss.item() * X.size(0)

            for i in range(len(Y)):

                actual = Y[i].item()

                prediction = predictions[i].item()

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

                    f"Správně: {actual} | "

                    f"Rozpoznáno: {prediction} | "

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


    print("\nMATICE ZÁMĚN")
    print("Řádky = skutečnost, sloupce = predikce")

    print("     " + " ".join(f"{i:4d}" for i in range(10)))

    for i in range(10):
        print(
            f"{i}:   " +
            " ".join(f"{int(x):4d}" for x in confusion_matrix[i])
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


# ==========================================
# TRÉNOVÁNÍ
# ==========================================

def train():

    training_data = load_training_data()

    if len(training_data) == 0:

        print("Trénovací dataset je prázdný!")

        return

    print("\n================================")
    print("DATASET")
    print("================================")

    print(f"Training: {len(training_data)}")

    print("================================")

    training_dataset = NumberDataset(
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

    if checkpoint is not None:

        if "optimizer_state_dict" in checkpoint:

            optimizer.load_state_dict(
                checkpoint["optimizer_state_dict"]
            )
        for param_group in optimizer.param_groups:
            param_group["lr"] = LEARNING_RATE

        start_epoch = checkpoint.get("epoch", 0)

        print(f"Pokračuji od epochy {start_epoch + 1}")

    # ======================================
    # EPOCHS
    # ======================================

    for epoch in range(
        start_epoch,
        start_epoch + EPOCHS
    ):

        print("\n========================================")

        print(f"EPOCH: {epoch + 1}")

        print("========================================")

        train_loss, train_accuracy, train_correct, train_incorrect = train_epoch(

            model,

            training_loader,

            optimizer,

            criterion,

            epoch + 1

        )

        print("\n--- TRAINING VÝSLEDKY ---")

        print(f"Train Loss: {train_loss:.6f}")

        print(f"Správně: {train_correct}")

        print(f"Špatně: {train_incorrect}")

        print(f"Train Accuracy: {train_accuracy:.2f}%")

        # Uložení modelu po každé epoše

        torch.save({

            "model_state_dict": model.state_dict(),

            "optimizer_state_dict": optimizer.state_dict(),

            "epoch": epoch + 1

        }, MODEL_PATH)

        print("Model uložen!")

    print("\n========================================")

    print("TRÉNOVÁNÍ DOKONČENO")

    print("========================================")

# ==========================================
# SAMOSTATNÁ VALIDACE
# ==========================================

def evaluate_model():

    if not os.path.exists(MODEL_PATH):

        print("Model nebyl nalezen!")

        return

    validation_data = load_validation_data()

    if not validation_data:

        print("Validační dataset je prázdný!")

        return

    model = NeuralNetwork().to(DEVICE)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=True
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    dataset = NumberDataset(
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

    for digit in range(OUTPUT_SIZE):

        if class_total[digit] > 0:

            digit_accuracy = (
                class_correct[digit] /
                class_total[digit] * 100
            )

            print(
                f"Číslice {digit}: "
                f"{digit_accuracy:.2f}% "
                f"({class_correct[digit]}/"
                f"{class_total[digit]})"
            )

    print("========================================")


# ==========================================
# HLAVNÍ PROGRAM
# ==========================================

if __name__ == "__main__":

    # "train" = pouze trénování
    # "validate" = pouze validace

    MODE = "validate"

    if MODE == "train":

        train()

    elif MODE == "validate":

        evaluate_model()

    else:

        print("Neznámý režim!")
