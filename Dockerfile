FROM tensorflow/tensorflow:2.8.0-gpu

WORKDIR /app

COPY *.py /app/
COPY requirements.txt /app/

RUN apt-get update -y && apt install libgl1-mesa-glx -y && apt-get install 'ffmpeg' 'libsm6' 'libxext6' -y

RUN pip install --upgrade pip && pip3 install -r requirements.txt

CMD ["python3", "learn.py", "headless"]
