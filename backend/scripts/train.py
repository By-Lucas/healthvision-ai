"""Fine-tune a chest X-ray classifier on your own images.

This trains a ResNet18 (ImageNet-pretrained) on a 2-class dataset and saves the
weights so the app can use them: set USE_MOCK_INFERENCE=false and
MODEL_WEIGHTS_PATH=<output> — the predictor then prefers these weights over the
generic torchxrayvision model.

Expected dataset layout (torchvision ImageFolder):

    data/
      NORMAL/      *.jpg / *.png
      PNEUMONIA/   *.jpg / *.png

Note: classes are read alphabetically, so NORMAL=0 and PNEUMONIA=1 — matching the
order the inference engine expects.

Requires the ML extras (installed in the Docker image):
    pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision

Usage:
    python -m scripts.train --data-dir ./data --out ./weights/model.pt --epochs 5
"""
from __future__ import annotations

import argparse
from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)

EXPECTED_CLASSES = ["NORMAL", "PNEUMONIA"]
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fine-tune a chest X-ray classifier.")
    p.add_argument(
        "--data-dir", required=True, help="ImageFolder root (NORMAL/, PNEUMONIA/)"
    )
    p.add_argument("--out", default="weights/model.pt", help="Output weights path")
    p.add_argument("--epochs", type=int, default=5)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--lr", type=float, default=1e-4)
    return p.parse_args()


def main() -> int:
    args = parse_args()

    # Heavy imports kept local so the script only needs torch when actually run.
    import torch
    from torch import nn
    from torch.utils.data import DataLoader
    from torchvision import datasets, models, transforms

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Training on %s", device)

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )
    dataset = datasets.ImageFolder(args.data_dir, transform=transform)
    logger.info("Found %d images, classes=%s", len(dataset), dataset.classes)
    if dataset.classes != EXPECTED_CLASSES:
        logger.warning(
            "Classes %s != expected %s. Inference assumes index 0=NORMAL, "
            "1=PNEUMONIA; rename folders to match.",
            dataset.classes,
            EXPECTED_CLASSES,
        )

    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, 2)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    model.train()
    for epoch in range(1, args.epochs + 1):
        running, correct, total = 0.0, 0, 0
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running += loss.item() * images.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)
        logger.info(
            "Epoch %d/%d — loss=%.4f acc=%.3f",
            epoch,
            args.epochs,
            running / max(total, 1),
            correct / max(total, 1),
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_path)
    logger.info("Saved weights to %s", out_path)
    logger.info(
        "To use it: set USE_MOCK_INFERENCE=false and MODEL_WEIGHTS_PATH=%s", out_path
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
