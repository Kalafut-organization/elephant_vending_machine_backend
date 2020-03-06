FROM python:3.8
WORKDIR /usr/src/elephant_vending_machine
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "elephant_vending_machine:APP"]
