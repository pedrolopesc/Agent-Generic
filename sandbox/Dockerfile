FROM python:3.11-slim
RUN pip install --no-cache-dir pytest ruff platformio
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
WORKDIR /workspace
USER 65534:65534
CMD ["python", "--version"]
