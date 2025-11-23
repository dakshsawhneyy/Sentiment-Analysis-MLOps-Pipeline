FROM python:3.10-slim AS builder

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY requirements.txt .

RUN python3 -m venv $VIRTUAL_ENV
RUN pip install --no-cache-dir -r requirements.txt

COPY src/trainer/train_baseline.py train_baseline.py

FROM python:3.10-slim
WORKDIR /app

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:PATH"

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
COPY --from=builder /app/train_baseline.py .

CMD ["python", "train_baseline.py"]