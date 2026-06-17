FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# OpenCV needs a couple of shared libs even in headless mode.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --upgrade pip && pip install -r requirements-dev.txt

# Real AI model stack. Installed separately so the CPU-only torch build is used
# (much smaller than the default CUDA wheels) and so CI unit tests — which run
# against the mock — don't need to pull these heavy packages.
# torch 2.4+ is required for NumPy 2.x compatibility (the app pins numpy 2.1).
RUN pip install --index-url https://download.pytorch.org/whl/cpu \
        torch==2.4.1 torchvision==0.19.1 \
    && pip install torchxrayvision==1.2.1 scikit-image

# Pre-download the pretrained chest X-ray weights into the image so the first
# inference is fast and a bad weights name fails the build, not production.
RUN python -c "import torchxrayvision as xrv; xrv.models.DenseNet(weights='densenet121-res224-all')"

COPY . .

# Create the uploads directory (also mounted as a volume in compose).
RUN mkdir -p /data/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
