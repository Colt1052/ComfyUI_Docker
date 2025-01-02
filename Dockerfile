FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive PIP_PREFER_BINARY=1

RUN apt-get update && apt-get install -y git && apt-get clean
RUN apt-get update && apt-get install -y iputils-ping
RUN apt-get -y install curl

ENV ROOT=/stable-diffusion

COPY requirements.txt ${ROOT}/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/ltdrdata/ComfyUI-Manager ${ROOT}/custom_nodes/ComfyUI-Manager && \
  pip install -r ${ROOT}/custom_nodes/ComfyUI-Manager/requirements.txt

RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git ${ROOT}/custom_nodes/ComfyUI-Custom-Scripts && \
  pip install -r ${ROOT}/custom_nodes/ComfyUI-Manager/requirements.txt

RUN git clone https://github.com/Fannovel16/comfyui_controlnet_aux/ ${ROOT}/custom_nodes/comfyui_controlnet_aux && \
  pip install -r ${ROOT}/custom_nodes/comfyui_controlnet_aux/requirements.txt

RUN git clone https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes.git ${ROOT}/custom_nodes/Derfuu_ComfyUI_ModdedNodes.git

RUN git clone https://github.com/jesenzhang/ComfyUI_StreamDiffusion.git ${ROOT}/custom_nodes/ComfyUI_StreamDiffusion

RUN git clone https://github.com/jags111/efficiency-nodes-comfyui.git ${ROOT}/custom_nodes/efficiency-nodes-comfyui && \
  pip install -r ${ROOT}/custom_nodes/efficiency-nodes-comfyui/requirements.txt

RUN git clone https://github.com/Limitex/ComfyUI-Diffusers.git ${ROOT}/custom_nodes/ComfyUI-Diffusers && \
  pip install -r ${ROOT}/custom_nodes/ComfyUI-Diffusers/requirements.txt
RUN git clone https://github.com/cumulo-autumn/StreamDiffusion.git ${ROOT}/custom_nodes/ComfyUI-Diffusers/StreamDiffusion && \
  pip install streamdiffusion[tensorrt] && \
  cd ${ROOT}/custom_nodes/ComfyUI-Diffusers/StreamDiffusion && \
  pip install --force-reinstall -v "huggingface_hub==0.25.0" && \
  pip install --force-reinstall torchvision --index-url https://download.pytorch.org/whl/cu121 && \
  #python -m ${ROOT}/custom_nodes/ComfyUI-Diffusers/StreamDiffusion/src/streamdiffusion/tools/install-tensorrt
  python -m streamdiffusion.tools.install-tensorrt
  


WORKDIR ${ROOT}
COPY . ${ROOT}

ENV NVIDIA_VISIBLE_DEVICES=all PYTHONPATH="${PYTHONPATH}:${PWD}" CLI_ARGS=""
EXPOSE 7860
EXPOSE 8188
CMD python -u main.py --listen --port 7860 ${CLI_ARGS}
