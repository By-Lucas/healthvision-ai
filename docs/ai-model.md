# AI model & inference pipeline

> Educational/portfolio project. The model output is a demonstration and must
> never inform real medical decisions.

## Goal

Classify a chest X-ray image into one of three classes:

- `NORMAL`
- `PNEUMONIA`
- `UNCERTAIN` (model not confident enough)

## Engines behind one port

The inference layer is designed around a **port** (`AIInferenceService`) with
interchangeable implementations that all return the **same `Prediction` value
object**:

```
AIInferenceService (abstract)
├── TorchXRayVisionEngine   # DEFAULT in Docker — real pretrained chest X-ray model
├── TorchInferenceEngine    # optional — loads your own fine-tuned weights file
└── MockInferenceEngine     # fallback — deterministic, dependency-light
```

`build_inference_engine()` selects one at runtime. With `USE_MOCK_INFERENCE=false`
(the Docker default) it tries **torchxrayvision** first, then a local weights
file, then falls back to the mock. Because the contract is identical, swapping
engines changes **zero lines** in the use cases, API, worker or frontend.

### Real model: torchxrayvision (default in Docker)

`TorchXRayVisionEngine` loads a **DenseNet (`densenet121-res224-all`)** pretrained
by [torchxrayvision](https://github.com/mlmed/torchxrayvision) on a union of large
public chest X-ray datasets (NIH, CheXpert, MIMIC, RSNA, …). It is **multi-label**:
one sigmoid probability per pathology. We read the pathologies that indicate
pneumonia on a film — `Pneumonia`, `Consolidation`, `Lung Opacity` — take the
strongest signal, and map it to our three classes:

| pneumonia/opacity score | class       |
|-------------------------|-------------|
| ≥ `XRAY_PNEUMONIA_HIGH` (0.50) | `PNEUMONIA` |
| ≤ `XRAY_PNEUMONIA_LOW` (0.35)  | `NORMAL`    |
| in between              | `UNCERTAIN` |

The thresholds are env-configurable (`XRAY_PNEUMONIA_HIGH` / `XRAY_PNEUMONIA_LOW`)
so you can tune sensitivity. The weights (~30 MB) are **pre-downloaded into the
Docker image** so the first inference is fast.

### Why a mock still exists

The mock keeps the project **fully runnable without torch** (e.g. CI unit tests,
or a quick clone without the heavy ML stack). It is **not a classifier** — it
derives a deterministic value from image brightness purely so the *pipeline*
(upload → queue → inference → dashboard) works end to end. Set
`USE_MOCK_INFERENCE=true` to force it.

## The pipeline

```
raw bytes
   │  Pillow: verify it is a real image (validation service)
   ▼
preprocessing.py
   │  OpenCV resize → 224×224, scale to [0,1], ImageNet normalization
   ▼
inference engine
   │  Mock:  brightness signature → 2 logits
   │  Torch: ResNet18 (fc → 3 classes) forward pass
   ▼
softmax → probabilities
   │  uncertainty gate: top prob < threshold ⇒ UNCERTAIN
   ▼
Prediction(predicted_class, confidence_score, processing_time_ms, class_probabilities)
```

### Mock engine details

The mock derives a **stable, deterministic** pseudo-probability from a cheap
image feature (mean brightness, a loosely radiographic signal). The same image
always yields the same prediction — important for reproducible demos, seeding and
e2e tests — while different images produce different results. Crucially, its
output *shape* (class + calibrated-looking confidence + per-class probabilities)
matches a real classifier.

### Custom fine-tuned weights

`model_loader.try_load_real_model()` will, when `USE_MOCK_INFERENCE=false` and
`MODEL_WEIGHTS_PATH` points at a checkpoint:

1. lazily import `torch` / `torchvision` (kept optional so the project runs
   without them);
2. build a `ResNet18` with the final layer resized to 2 classes
   (NORMAL, PNEUMONIA — UNCERTAIN comes from the confidence gate);
3. load the state dict and switch to eval mode.

If anything is missing or fails, it logs a warning and **falls back** to the
torchxrayvision model, then to the mock — the system never hard-crashes.

## Training your own model (`scripts/train.py`)

You don't have to train — the pretrained torchxrayvision model is strong. But if
you want to fine-tune on your own labelled images:

1. Arrange your data as an ImageFolder:
   ```
   data/
     NORMAL/      *.jpg / *.png
     PNEUMONIA/   *.jpg / *.png
   ```
2. Run the fine-tuning script (uses an ImageNet-pretrained ResNet18):
   ```bash
   make train DATA=./data OUT=./weights/model.pt
   # or directly: python -m scripts.train --data-dir ./data --out ./weights/model.pt --epochs 5
   ```
3. Point the app at the weights and restart the worker:
   ```env
   USE_MOCK_INFERENCE=false
   MODEL_WEIGHTS_PATH=/data/weights/model.pt
   ```
   When `MODEL_WEIGHTS_PATH` exists it **takes precedence** over the generic
   torchxrayvision model. No code changes required.

**Recommendation:** a model trained on a small folder usually performs *worse*
than the pretrained one (which saw hundreds of thousands of images). Prefer the
pretrained model unless you have a substantial, well-curated dataset.

## Metrics (scikit-learn)

`scikit-learn` is included for offline evaluation of a trained model
(accuracy, precision/recall, confusion matrix). A natural next step is to surface
these metrics on the dashboard alongside live usage stats.

## Responsible-AI notes

- The **uncertainty gate** prevents the system from emitting an overconfident
  class on weak signal.
- Every result carries an **educational warning** (`Analysis.warning`), shown in
  the API response and the UI.
- Explanations are deliberately **plain-language and non-clinical**.
