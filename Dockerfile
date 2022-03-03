FROM alpine:3.14

# Install OCR related needs
RUN apk add imagemagick
# By default, it has no grants on PDF
RUN sed -i 's/  <!-- <policy domain="module" rights="none" pattern="{PS,PDF,XPS}" \/> -->/  <policy domain="module" rights="read|write" pattern="{PS,PDF,XPS}" \/>/g' /etc/ImageMagick-7/policy.xml
RUN apk add tesseract-ocr

RUN mkdir /logs
RUN mkdir /bra

# Install python/pip/poetry
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add python3-dev gcc musl-dev libffi libffi-dev
RUN python3 -m ensurepip
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install wheel
RUN python3 -m pip install poetry
RUN poetry --version
