# -----------------------------------------------------------------------------
# Builder image, it creates the wheels to install to the final images
# -----------------------------------------------------------------------------
FROM python:3.12.2-bullseye AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
&& apt-get -y install build-essential

# Compile Python dependencies to wheels
COPY requirements.txt .

RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 wheel --no-cache-dir --no-deps --wheel-dir /usr/src/wheels -r requirements.txt

# -----------------------------------------------------------------------------
# Main image, it has the shared layers between development and production
# -----------------------------------------------------------------------------
FROM python:3.12.2-slim-bullseye AS main

# Universal buffer workaround (refer to Python base image for details)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Python ENV
ENV PYTHONPATH=/home/app/

# Install netcat to run the entrypoint.sh, and libpq to connect to Postgres
RUN apt-get update \
&& apt-get -y install gcc libpq-dev

# Create app directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/
RUN mkdir -p $APP_HOME && mkdir -p $HOME

# Install the wheels compiled in the builder image
COPY --from=builder /usr/src/wheels /wheels
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache /wheels/*
RUN rm -rf /wheels

# -----------------------------------------------------------------------------
# Development image, includes a SSH keygen server, inherited from the original image
# -----------------------------------------------------------------------------
FROM main AS development

RUN apt-get update

WORKDIR /home/app/

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]

# -----------------------------------------------------------------------------
# Production image, includes the application files
# -----------------------------------------------------------------------------
FROM main AS production

WORKDIR /home/app/

# Copy the rest of the application code into the container
COPY . .

