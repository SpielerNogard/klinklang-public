FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

LABEL maintainer="Christopher Müller <christopher.m4120@gmail.com>"
RUN apt-get update &&  apt-get install -y git

COPY email_reader/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY src /tmp/src
RUN pip install /tmp/src

WORKDIR /app/

COPY email_reader /app
COPY src /tmp/src



ENV PYTHONPATH=/app
CMD ["python", "index.py"]