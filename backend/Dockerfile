FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV BACKEND_PORT=3001
ENV K8S_ENABLED=true
ENV DOCKER_ENABLED=true
ENV HOME=/root

EXPOSE 3001

CMD ["python", "main.py"]
