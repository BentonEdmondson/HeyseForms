FROM python:3.10-slim

WORKDIR /src

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8000
COPY . .
CMD ["gunicorn", "-c", "guniconf.py", "main:app"]
