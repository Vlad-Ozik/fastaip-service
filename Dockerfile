FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

ENV SLACK_TOKEN="your slack token"
ENV SHARED_SECRET="opapa"
ENV GOOGLE_APPLICATION_CREDENTIALS="path to json with credentials"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]