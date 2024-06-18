#!/usr/bin/env bash

echo "Worker Initiated"
echo "Symlinking files from Network Volume"
rm -rf /workspace && \
  ln -s /runpod-volume /workspace

echo "Activating Virtual Environment"
source /workspace/venv/bin/activate
TCMALLOC="$(ldconfig -p | grep -Po "libtcmalloc.so.\d" | head -n 1)"
export LD_PRELOAD="${TCMALLOC}"
export PYTHONUNBUFFERED=true
export HF_HOME="/workspace"
cd /workspace/ComfyUI

# Serve the API and don't shutdown the container
if [ "$SERVE_API_LOCALLY" == "true" ]; then
    echo "runpod-worker-comfy: Starting ComfyUI"
    python main.py --disable-auto-launch --disable-metadata --listen &
    deactivate

    echo "runpod-worker-comfy: Starting RunPod Handler"
    python -u /rp_handler.py --rp_serve_api --rp_api_host=0.0.0.0
else
    echo "runpod-worker-comfy: Starting ComfyUI from VENV"
    python main.py --disable-auto-launch --disable-metadata > /workspace/ComfyUI/log/comfyui.log 2>&1 &
    deactivate

    echo "runpod-worker-comfy: Starting RunPod Handler outside of VENV"
    python -u /rp_handler.py > /workspace/ComfyUI/log/rp_handler.log 2>&1
fi