FROM ubuntu:22.04
LABEL authors="Mateusz"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/backend/ \
    PYTHONPATH=/backend/backendapp

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    libusb-1.0-0-dev \
    usbutils \
    git \
    ssh \
    curl \
    iputils-ping \
    uwsgi-core \
    uwsgi-plugin-python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR $APP_HOME

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /backend/backendapp
COPY wsgi.py /backend/
COPY requirements.txt /backend/
COPY uwsgi.ini /backend/

RUN usermod -a -G dialout,plugdev root

EXPOSE 5000

CMD ["uwsgi", "--ini", "uwsgi.ini"]