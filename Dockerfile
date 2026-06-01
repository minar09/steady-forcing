# =========================================================
# Base: CUDA 12.1 + Ubuntu 22.04
# =========================================================
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# =========================================================
# Environment
# =========================================================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    MAX_JOBS=4

# =========================================================
# System dependencies
# =========================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3.10-venv \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    wget \
    build-essential \
    ninja-build \
    cmake \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# =========================================================
# Ensure python + pip consistency
# =========================================================
RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    python -m pip install --upgrade pip setuptools wheel

# =========================================================
# Install PyTorch (CUDA 12.1)  ✅ FIXED
# =========================================================
RUN python -m pip install \
    torch==2.5.1 \
    torchvision==0.20.1 \
    torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cu121

# =========================================================
# Core build helpers
# =========================================================
RUN python -m pip install psutil ninja

# =========================================================
# NVIDIA packages
# =========================================================
RUN python -m pip install --extra-index-url https://pypi.nvidia.com nvidia-tensorrt

# =========================================================
# CUDA / Performance Libraries
# (flash-attn AFTER torch install)
# =========================================================
RUN python -m pip install \
    triton==3.1.0 \
    xformers \
    bitsandbytes \
    deepspeed

# flash-attn separately (more stable build)
RUN python -m pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/flash_attn-2.8.3+cu12torch2.5cxx11abiFALSE-cp310-cp310-linux_x86_64.whl --no-build-isolation

# =========================================================
# CLIP
# =========================================================
RUN python -m pip install git+https://github.com/openai/CLIP.git --no-build-isolation

# =========================================================
# Requirements
# =========================================================
COPY <<EOF /tmp/requirements.txt
numpy==1.26.4
pandas
scipy
tqdm
requests
aiohttp

opencv-python>=4.9.0.80
pillow
imageio
imageio-ffmpeg
av==13.1.0
decord
albumentations
albucore
scikit-image

diffusers==0.31.0
tokenizers>=0.20.3
datasets
einops
scikit-learn
sentencepiece

wandb
easydict
ftfy
omegaconf
ml_collections
absl-py

huggingface_hub[cli]
openai
dashscope

flask
flask-socketio
fastapi
uvicorn
starlette

lmdb
pycocotools

matplotlib

pydantic==2.10.6
dominate

onnx
onnxruntime
onnxscript
onnxconverter_common
nvidia-tensorrt
pycuda

nvidia-ml-py

open_clip_torch

safetensors
timm
sentencepiece
peft==0.11.1
torchao==0.7.0

easydict
ml_collections
absl-py
dashscope

transformers==4.45.2
trl==0.8.6
accelerate==0.34.0

EOF

RUN python -m pip install -r /tmp/requirements.txt

# =========================================================
# Workdir
# =========================================================
WORKDIR /workspace/static-forcing

# =========================================================
# Copy project
# =========================================================
COPY . .

# =========================================================
# Install project
# =========================================================
RUN python setup.py develop

# ADD before CMD ["bash"]:
RUN git clone https://github.com/KwaiVGI/VideoAlign /workspace/VideoAlign && \
    python -m pip install -e /workspace/VideoAlign --no-deps

# =========================================================
# Default
# =========================================================
CMD ["bash"]