FROM python:3.9-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder /app /app

RUN mkdir -p /data

VOLUME ["/data"]

ENTRYPOINT ["twint"]
CMD ["--help"]
