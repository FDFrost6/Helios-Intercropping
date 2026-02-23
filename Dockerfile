# Helios Intercropping Pipeline - GPU-Accelerated Docker Image
#
# Base image: NVIDIA CUDA 12.3 + cuDNN 8 on Ubuntu 22.04
# Provides: CUDA toolkit, compiler toolchain, CMake, Python 3.10,
#           OptiX 7.x SDK (driver-bundled), PyHelios, and all Python deps.
#
# Build:
#   docker build -t helios-intercropping .
#
# Run (requires NVIDIA Container Toolkit):
#   docker run --gpus all -it --rm \
#     -v "$(pwd)/output:/workspace/output" \
#     helios-intercropping python scripts/generate_scene.py --help

ARG CUDA_VERSION=12.3.2
ARG UBUNTU_VERSION=22.04

FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}

LABEL maintainer="Helios Intercropping Pipeline"
LABEL description="GPU-accelerated plant imaging pipeline (CUDA + OptiX + PyHelios)"

# ── System dependencies ────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        ninja-build \
        git \
        wget \
        curl \
        ca-certificates \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        python3.10 \
        python3.10-dev \
        python3.10-venv \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Make python3.10 the default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/python  python  /usr/bin/python3.10 1 \
    && pip3 install --no-cache-dir --upgrade pip setuptools wheel

# ── OptiX 7 note ──────────────────────────────────────────────────────────────
# NVIDIA OptiX 7.x is distributed as a closed-source SDK that requires a free
# NVIDIA Developer Program account and cannot be redistributed inside a Docker
# image.  The NVIDIA Container Toolkit makes the host driver's liboptix.so
# available inside the container at runtime, so no separate installation step
# is needed as long as the host driver is ≥ 520 (OptiX 7.6+).
#
# To install the OptiX SDK headers for *building* PyHelios from source:
#   1. Download NVIDIA-OptiX-SDK-7.7.0-linux64.sh from
#      https://developer.nvidia.com/designworks/optix/download
#   2. Pass it as a build-arg:
#        docker build --build-arg OPTIX_INSTALLER=/path/to/installer.sh \
#                     -t helios-intercropping .
ARG OPTIX_INSTALLER=""
ENV OPTIX_INSTALL_DIR=/opt/optix
RUN if [ -n "${OPTIX_INSTALLER}" ] && [ -f "${OPTIX_INSTALLER}" ]; then \
        chmod +x "${OPTIX_INSTALLER}" \
        && "${OPTIX_INSTALLER}" --skip-license --prefix="${OPTIX_INSTALL_DIR}" \
        && echo "OptiX SDK installed to ${OPTIX_INSTALL_DIR}"; \
    else \
        echo "OptiX installer not provided; runtime liboptix.so supplied by NVIDIA Container Toolkit."; \
    fi

# ── CUDA environment variables ─────────────────────────────────────────────────
ENV CUDA_HOME=/usr/local/cuda
ENV PATH="${CUDA_HOME}/bin:${PATH}"
ENV LD_LIBRARY_PATH="${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}"

# ── PyHelios ───────────────────────────────────────────────────────────────────
WORKDIR /opt
RUN git clone --depth 1 https://github.com/PlantSimulationLab/PyHelios.git && \
    cd PyHelios && \
    pip3 install --no-cache-dir -e .

# ── Application ───────────────────────────────────────────────────────────────
WORKDIR /workspace
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN pip3 install --no-cache-dir -e .

# Output directory
RUN mkdir -p /workspace/output
VOLUME ["/workspace/output"]

# ── Default command ────────────────────────────────────────────────────────────
CMD ["python", "scripts/generate_scene.py", "--help"]
