# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /application

# Copy requirements.txt and install the Python packages
COPY requirements.txt /application/requirements.txt
RUN pip install --upgrade -r /application/requirements.txt

# Copy the rest of the application
COPY . /application/

ENV APP_PATH=/application

CMD ["uvicorn", "application.main:app", "--host", "0.0.0.0", "--port", "8000"]