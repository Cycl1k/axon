FROM python:3.11.6

WORKDIR /src

ENV PYTHNDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY ./app app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]