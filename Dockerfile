FROM ubuntu:20.04

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
RUN apt-get install -y python3.9 --fix-missing && ln -sf python3.9 /usr/bin/python3
RUN python3 --version
RUN apt-get install -y python3-dev gcc musl-dev libffi-dev python3-pip apt-utils
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install wheel poetry cryptography
RUN poetry --version
COPY poetry.lock pyproject.toml /app/

# OpenCV dependencies
RUN apt-get install -y ffmpeg libsm6 libxext6

# Copy runtime files
ADD ./bra_database /app/bra_database
ADD ./run.py /app/run.py
ADD ./run.sh /app/run.sh

# Add env variables containing DB info
ADD . ${MYSQL_USER}
ADD . ${MYSQL_PWD}
ADD . ${MYSQL_HOST}
ADD . ${MYSQL_PORT}
ADD . ${MYSQL_DB}
ADD . ${MYSQL_TABLE}

# Install the dependencies in the python system
WORKDIR /app
RUN ls -alstrh
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev

CMD ["./run.sh"]
