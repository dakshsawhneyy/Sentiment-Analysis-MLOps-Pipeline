FROM python:3.10-slim AS builder

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY requirements.txt .

RUN python3 -m venv $VIRTUAL_ENV
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ingestor/ingestor.py ingestor.py

FROM python:3.10-slim
WORKDIR /app

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:PATH"

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
COPY --from=builder /app/ingestor.py .

CMD ["python", "ingestor.py"]