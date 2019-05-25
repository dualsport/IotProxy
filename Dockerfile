FROM python:3.7-slim-stretch

WORKDIR /app

COPY IotProxy.py /app
COPY requirements.txt /app
COPY settings.py /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80

ENV HOST 0.0.0.0
ENV LISTENING_PORT 80
ENV MAX_CONN 5
ENV BUFFER_SIZE 4096

CMD ["python", "-u", "IotProxy.py"]

