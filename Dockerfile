# Stage 1: Build dashboard
FROM node:20-slim AS dashboard-build
WORKDIR /app/dashboard
COPY dashboard/package.json dashboard/package-lock.json ./
RUN npm ci --no-audit
COPY dashboard/ ./
RUN npm run build

# Stage 2: Backend + serve dashboard
FROM python:3.11-slim
WORKDIR /app

# System dependencies for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY backend/ backend/
COPY test_madara.py ./
COPY scripts/ scripts/

# Copy built dashboard
COPY --from=dashboard-build /app/dashboard/dist dashboard/dist

# Create required directories
RUN mkdir -p voice_samples/custom output/cache

# Agree to Coqui TOS for automated environments
ENV COQUI_TOS_AGREED=1
ENV VOICE_CLONER_GPU=0
ENV VOICE_CLONER_PRELOAD=0

EXPOSE 5000

CMD ["python", "backend/tts_server.py"]
