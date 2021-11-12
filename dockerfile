FROM python:3.8-buster
RUN mkdir -p /root/.ssh
COPY id_rsa /root/.ssh/id_rsa
RUN chmod 700 /root/.ssh/id_rsa
WORKDIR /usr/src/elephant_vending_machine
COPY . .
RUN apt-get -y update
RUN apt-get -y install cmake
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "elephant_vending_machine:APP"]
