FROM python:3.9-slim

WORKDIR /digital_bath

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5001

CMD [ "python", "app.py"]
