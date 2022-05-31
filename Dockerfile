FROM tensorflow/tensorflow:2.8.0-gpu

WORKDIR /app

COPY *.py /app/
COPY requirements.txt /app/

# fix nvidia repo
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub

RUN apt-get update -y && apt install libgl1-mesa-glx -y && apt-get install 'ffmpeg' 'libsm6' 'libxext6' -y

RUN pip install --upgrade pip && pip3 install -r requirements.txt

CMD ["python3", "learn.py", "headless"]
