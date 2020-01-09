FROM python:3.8-alpine

RUN apk add --no-cache libffi-dev build-base openssl-dev

RUN gcc --version

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del libffi-dev build-base openssl-dev

COPY ./LICENSE .
COPY ./README.md .

COPY ./src ./src

CMD [ "python", "./src/issuesbot/main.py" ]
