FROM python:3.7-slim-stretch

WORKDIR /app

COPY IotProxy.py /app
COPY requirements.txt /app
COPY settings.py /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8080

ENV HOST
ENV LISTENING_PORT 8080
ENV MAX_CONN 5
ENV BUFFER_SIZE 2048

CMD ["python", "IotProxy.py"]

