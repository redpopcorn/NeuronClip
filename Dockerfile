FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set up user 1000 to match Hugging Face Spaces requirements
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user/app/src

WORKDIR /home/user/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code
COPY --chown=user src/ ./src/
COPY --chown=user server/ ./server/

EXPOSE 7860

# Run FastAPI server on port 7860 (Hugging Face default)
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860"]
