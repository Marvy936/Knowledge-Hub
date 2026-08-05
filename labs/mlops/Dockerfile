FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MLOPS_WORKSPACE=/state

WORKDIR /app

COPY labs/machine-learning /app/machine-learning
COPY labs/mlops /app/mlops

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir /app/machine-learning /app/mlops

EXPOSE 8080

CMD ["uvicorn", "mlops_lab.service:app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
