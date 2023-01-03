FROM ubuntu:20.04

ARG MYSQL_USER
ARG MYSQL_PWD
ARG MYSQL_HOST
ARG MYSQL_PORT
ARG MYSQL_DB
ARG MYSQL_TABLE

RUN apt-get update
RUN apt-get install -y apt-utils

# Install OCR related needs
RUN apt-get install -y imagemagick

# By default, it has no grants on PDF
RUN sed -i 's/  <policy domain="coder" rights="none" pattern="PDF" \/>/  <policy domain="coder" rights="read|write" pattern="PDF" \/>/g' /etc/ImageMagick-6/policy.xml
RUN echo "====" && cat /etc/ImageMagick-6/policy.xml | grep "PDF" && echo "===="
RUN apt-get install -y tesseract-ocr

RUN mkdir -p /logs /bra /app /img

# Install python/pip/poetry
ENV PYTHONUNBUFFERED=1
RUN apt-get update
RUN apt-get install -y python3.9 --fix-missing && \
    ln -sf python3.9 /usr/bin/python3
RUN python3 --version
RUN apt-get install -y \
    python3-dev \
    gcc \
    musl-dev \
    libffi-dev \
    python3-pip \
    ffmpeg \
    libsm6 \
    libxext6 \
    libmagickwand-dev
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install \
    wheel \
    poetry \
    cryptography
RUN poetry --version
COPY poetry.lock pyproject.toml /app/

# Copy runtime files
ADD ./bra_database /app/bra_database
ADD ./run.py /app/run.py
ADD ./scripts/run.sh /app/run.sh

# Add env variables containing DB info
ENV MYSQL_USER ${MYSQL_USER}
ENV MYSQL_PWD ${MYSQL_PWD}
ENV MYSQL_HOST ${MYSQL_HOST}
ENV MYSQL_PORT ${MYSQL_PORT}
ENV MYSQL_DB ${MYSQL_DB}
ENV MYSQL_TABLE ${MYSQL_TABLE}
ENV MYSQL_TABLE ${MYSQL_TABLE}

# Install the dependencies in the python system
WORKDIR /app
RUN ls -alstrh
RUN poetry config virtualenvs.in-project true
RUN poetry install --only main

EXPOSE 3306

CMD ["./run.sh"]
