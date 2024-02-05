# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /application

ADD ./application /application

COPY requirements.txt /application/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade -r /application/requirements.txt

COPY . /application/

ENV APP_PATH=/application/

CMD ["uvicorn", "application.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]