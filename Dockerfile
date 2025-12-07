FROM python:3.11-slim


# install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Ruff
RUN pip install --no-cache-dir ruff

COPY /app /app
WORKDIR /app

RUN ruff check .

CMD ["python", "sensor_container.py"]