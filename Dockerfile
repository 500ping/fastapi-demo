FROM python:3.10.13-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app

RUN chmod +x /app/entrypoint.sh
CMD [ "sh", "/app/entrypoint.sh" ]