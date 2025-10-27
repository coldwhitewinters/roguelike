FROM python:3.12-slim

# Python environment optimization settings:
# - PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files to disk
# - PYTHONUNBUFFERED=1: Forces Python stdout/stderr to be unbuffered for real-time output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1    

RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set UV cache directory and disable hardlinks to avoid warnings
ENV UV_CACHE_DIR=/tmp/uv-cache \
    UV_LINK_MODE=copy

# Install Claude Code
RUN curl -fsSL claude.ai/install.sh | bash

WORKDIR /workspace

EXPOSE 8000

CMD ["/bin/bash"]