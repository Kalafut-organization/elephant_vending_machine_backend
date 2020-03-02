FROM python:3.8
ADD . /elephant_vending_machine
WORKDIR /elephant_vending_machine
RUN pip install --upgrade pip
COPY ./requirements.txt /elephant_vending_machine/requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "elephant_vending_machine:APP"]
