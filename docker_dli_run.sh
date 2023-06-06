sudo docker run --runtime nvidia -it --rm --network host      --volume */nvdli-data:/nvdli-nano/data      --device /dev/video0      nvcr.io/nvidia/dli-nano-ai:v2.0.0-r32.4.3
