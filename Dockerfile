FROM python:3.7 as base

FROM base as install-poetry
RUN pip install poetry

FROM install-poetry as install-deps
WORKDIR /aiohttp-cache
COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN poetry install

FROM install-deps as copy-src
COPY . .

ENTRYPOINT ["poetry", "run"]
