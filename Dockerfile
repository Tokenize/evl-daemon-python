FROM python:3.13

WORKDIR /usr/src/app

RUN pip install poetry

COPY poetry.lock pyproject.toml ./

RUN poetry install

COPY . .

CMD [ "poetry", "run", "python3", "./evldaemon.py", "--config=config.json" ]