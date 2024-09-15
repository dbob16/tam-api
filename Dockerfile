FROM python:3.12.3

WORKDIR /tam
COPY ./requirements-server.txt /tam/requirements-server.txt
RUN pip install --no-cache-dir --upgrade -r requirements-server.txt

COPY ./server /tam/server
WORKDIR /tam/server
EXPOSE 80

CMD ["fastapi", "run", "main.py", "--proxy-headers", "--port", "80"]
HEALTHCHECK --interval=10s --timeout=3s CMD curl --fail http://loclahost:80/health/