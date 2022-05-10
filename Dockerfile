FROM python:3.10

WORKDIR /app

COPY *.py /app/
COPY requirements.txt /app/

RUN pip install --upgrade pip && pip3 install -r requirements.txt

CMD ["python3", "learn.py", "headless"]
