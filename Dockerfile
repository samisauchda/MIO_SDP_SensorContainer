# Stage 1: Lint and test
FROM python:3.11-slim AS lint

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install ruff for linting
RUN pip install --no-cache-dir ruff

# Copy application code
COPY /app /app

# Run linting
RUN ruff check .


# Stage 2: Production runtime
FROM python:3.11-slim AS production

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install only production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY /app /app
COPY config.example.yml /app/config.yml

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

CMD ["python", "sensor_container.py"]