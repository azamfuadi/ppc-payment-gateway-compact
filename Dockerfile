FROM python:3.7

EXPOSE 5000/tcp

WORKDIR /app

RUN apt-get update

RUN apt-get install ffmpeg libsm6 libxext6 -y

COPY requirements.txt .
COPY views/ /app/views/
COPY __pycache__/ /app/__pycache__/

RUN pip install -r requirements.txt

COPY app.py .

CMD ["python3", "app.py"]
