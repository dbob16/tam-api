FROM python:slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /tam
COPY ./requirements-server.txt /tam/requirements-server.txt
RUN pip install --no-cache-dir --upgrade -r requirements-server.txt

COPY ./server /tam/server
WORKDIR /tam/server
EXPOSE 80

CMD ["fastapi", "run", "main.py", "--proxy-headers", "--port", "80"]