FROM python:3.11.15-slim

ENV PYTHONUNBUFFERED=1

## Copy everything here first
WORKDIR /PortalSahayak-backend

## Then let's copy requirements.txt file
COPY requirements.txt .

## Then run it
RUN pip install --no-cache-dir -r requirements.txt

## Install chromium
RUN playwright install --with-deps chromium

# Then copy all other files there too
COPY . .

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]