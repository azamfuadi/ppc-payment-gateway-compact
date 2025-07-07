#Python package version
FROM python:3.7-slim

#Port that will be used
EXPOSE 5000/tcp

#Setting the working directory and installing necessary package
WORKDIR /app

RUN apt-get update

RUN apt-get install ffmpeg libsm6 libxext6 -y

COPY requirements.txt .
COPY views/ /app/views/
COPY __pycache__/ /app/__pycache__/

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

#Running the flask command
# CMD ["python3", "app.py"]
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
