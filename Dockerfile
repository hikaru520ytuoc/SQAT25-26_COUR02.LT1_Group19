FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY main.py .
COPY README.md .
COPY samples ./samples
COPY reports ./reports

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
