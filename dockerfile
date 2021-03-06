FROM continuumio/miniconda3

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install curl -y
RUN apt-get install build-essential libssl-dev libffi-dev unixodbc-dev -y
RUN pip install --upgrade pip setuptools wheel
RUN apt-get install build-essential -y

RUN conda install psutil -y

ADD requirements.txt /leafdevice/
RUN pip install -r /leafdevice/requirements.txt

COPY . /leafdevice/

# RUN mv /leafdevice/run.py /run.py

RUN chmod -x /leafdevice/run.py

# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED 1

CMD ["python", "/leafdevice/protocol_gateway.py"]