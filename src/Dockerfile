FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV FLASK_APP=endpoints/main.py
EXPOSE 5000
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]
