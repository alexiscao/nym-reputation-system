FROM python:3.11-slim

WORKDIR /nym-reputation-system

RUN apt-get update && \
    apt-get install -y python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["/bin/bash"]
