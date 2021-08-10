ARG PY_VERSION

FROM python:${PY_VERSION}-slim as base

FROM base as install-poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apt update -y
RUN apt install -y curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

ENV PATH "/root/.local/bin:$PATH"

COPY ./pyproject.toml .
COPY ./poetry.lock .

RUN poetry install


FROM base as target
COPY --from=install-poetry /.venv /.venv
WORKDIR /app
ENV PATH="/.venv/bin:$PATH"
COPY . .
