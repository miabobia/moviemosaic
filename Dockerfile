FROM python:3.12.1
RUN apt-get update && apt-get install -y sqlite3
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "server.py"]