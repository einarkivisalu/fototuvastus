FROM python:3.5.2

RUN apt-get -y update

RUN apt-get install -y \
    cmake \
    build-essential \
    libboost-all-dev \
    python3-dev
    
WORKDIR /app

ADD . /app

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python3", "photoQualityChecker.py"]