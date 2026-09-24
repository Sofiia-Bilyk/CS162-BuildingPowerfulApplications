FROM python:3.11.4-alpine3.17
LABEL maintainer="psterne@minerva.edu"

COPY requirements.txt .

# Install postgres libraries so that the pip install succeeds.
# We then immediately remove the unnecessary dependency.
RUN apk update && \
    apk add python3 postgresql-libs && \
    apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Make port 5162 available to the world outside this container
EXPOSE 5162

# Run app.py when the container launches
CMD ["python", "app.py"]
