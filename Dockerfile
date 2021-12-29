FROM tiangolo/uvicorn-gunicorn:python3.9

ENV PORT=8080

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./styles /app/styles/
COPY ./main.py /app/main.py
