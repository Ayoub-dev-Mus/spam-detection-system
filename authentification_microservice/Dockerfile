# syntax=docker/dockerfile:1

# Specify the base image with the desired Python version.
ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Set the working directory to /app.
WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install dependencies.
# Copy requirements.txt first to leverage Docker cache for dependencies.
COPY requirements.txt /app/

# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY src/authentification_microservice/ /app

# Set the environment variable for Django settings module if necessary.
# ENV DJANGO_SETTINGS_MODULE=authentification_microservice.settings

# Expose the port that the application listens on.
EXPOSE 8001

# Switch to the non-privileged user to run the application.
USER appuser

# Run the application with Gunicorn.
CMD ["gunicorn", "authentification_microservice.wsgi:application", "--bind", "0.0.0.0:8000"]
