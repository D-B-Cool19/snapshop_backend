FROM python:3.11-slim-buster
WORKDIR /app
RUN apt-get update && apt-get install -y libgl1-mesa-glx && apt-get install -y libglib2.0-0
RUN pip install --upgrade pip setuptools wheel
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD ["flask", "run"]