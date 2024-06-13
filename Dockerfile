# Use Nvidia CUDA base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 as base

# Prevents prompts from packages asking for user input during installation
ENV DEBIAN_FRONTEND=noninteractive
# Prefer binary wheels over source distributions for faster pip installations
ENV PIP_PREFER_BINARY=1
# Ensures output from python is printed immediately to the terminal without buffering
ENV PYTHONUNBUFFERED=1 

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /

# Upgrade apt packages and install required dependencies
RUN apt update && \
    apt upgrade -y && \
    apt install -y \
      python3-dev \
      python3-pip \
      fonts-dejavu-core \
      rsync \
      git \
      jq \
      moreutils \
      aria2 \
      wget \
      curl \
      libglib2.0-0 \
      libsm6 \
      libgl1 \
      libxrender1 \
      libxext6 \
      ffmpeg \
      libgoogle-perftools4 \
      libtcmalloc-minimal4 \
      procps && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean -y

# Clone ComfyUI repository
#RUN git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui

# Change working directory to ComfyUI
#WORKDIR /comfyui

#ARG SKIP_DEFAULT_MODELS
# Download checkpoints/vae/LoRA to include in image.
# RUN if [ -z "$SKIP_DEFAULT_MODELS" ]; then wget -O models/checkpoints/sd_xl_base_1.0.safetensors https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors; fi
# RUN if [ -z "$SKIP_DEFAULT_MODELS" ]; then wget -O models/vae/sdxl_vae.safetensors https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors; fi
# RUN if [ -z "$SKIP_DEFAULT_MODELS" ]; then wget -O models/vae/sdxl-vae-fp16-fix.safetensors https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors; fi

# Install ComfyUI dependencies
# RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 \
#     && pip3 install --no-cache-dir xformers==0.0.21 \
#     && pip3 install -r requirements.txt

# Install runpod
#RUN pip3 install runpod requests

# Support for the network volume
#ADD src/extra_model_paths.yaml ./

# Set Python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Install Worker dependencies
RUN pip install requests runpod

# Add the start and the handler
ADD src/start.sh src/rp_handler.py test_input.json ./
RUN chmod +x /start.sh

# Start the container
CMD /start.sh
