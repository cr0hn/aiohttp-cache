FROM python:3.7 as base

FROM base as install-deps
WORKDIR /aiohttp-cache

COPY ./requirements.txt .
COPY ./requirements-test.txt .

RUN pip install -r requirements.txt
RUN pip install -r requirements-test.txt

FROM install-deps as copy-src
COPY . .
