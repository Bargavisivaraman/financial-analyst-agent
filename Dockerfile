FROM python:3.12-slim

WORKDIR /app

# Install deps first for better layer caching
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY frontend ./frontend

ENV PORT=8000
EXPOSE 8000

# Render/Railway inject $PORT; server.py reads it.
CMD ["python", "-m", "backend.server"]
