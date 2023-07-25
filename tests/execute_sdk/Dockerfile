FROM python:3.10-buster

RUN : \
	&& apt-get -y update \
	&& apt-get -y upgrade \
	&& rm -rf /var/lib/apt/lists/*

RUN pip3 install poetry

WORKDIR "/home/app"
COPY [".", "."]
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN poetry config virtualenvs.create false
RUN poetry install
CMD [ "python3", "examples/simple_worker/main.py" ]
