ARG PY_VERSION
FROM python:$PY_VERSION-alpine as base

FROM base as install-poetry
RUN apk add --no-cache gcc musl-dev
RUN wget -O - https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="/root/.local/bin:/root/.poetry/bin:${PATH}"

FROM install-poetry as install-deps
WORKDIR /aiohttp-cache
COPY ./pyproject.toml .
COPY ./poetry.lock .

RUN poetry install

FROM install-deps as copy-src
COPY . .

ENTRYPOINT ["poetry", "run"]
