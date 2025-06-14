FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential libffi-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "src/main.py"]


