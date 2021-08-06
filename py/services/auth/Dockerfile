FROM python:3.6-alpine3.9 as base
FROM base as builder

RUN mkdir /install
WORKDIR /install

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# Install dependencies
RUN apk add --no-cache  \
        gcc \
        g++ \
        libc-dev \
        libffi-dev \
        linux-headers \
        musl-dev \
        openssl-dev

RUN pip install --upgrade pip

COPY requirements.txt /tmp/

RUN pip wheel --wheel-dir=/tmp/wheelhouse -r /tmp/requirements.txt
RUN pip install --prefix=/install -r /tmp/requirements.txt --no-index --find-links=/tmp/wheelhouse --no-warn-script-location

FROM base

# Install dependencies
RUN apk add --no-cache \
        bash \
        libssl1.1 \
        netcat-openbsd

COPY --from=builder /install /usr/local
COPY . /code/

WORKDIR /code/

CMD ["gunicorn", "auth.wsgi:app", "-b", ":8000"]
