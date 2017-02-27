FROM python:2.7-alpine
MAINTAINER Tom Grant <t.grant@outlook.com>

ENV INSTALL_PATH=/boilerroom-server

# Setup dependencies
RUN apk update --no-cache
RUN apk add --update --no-cache \
    curl \
    gcc \
    libffi-dev \
    libc-dev \
    mariadb-dev \
    nano \
    tar

# Pull modd for livereloading during development
RUN curl -sL https://github.com/cortesi/modd/releases/download/v0.4/modd-0.4-linux64.tgz | tar xz -C /bin --strip-components=1

# Set working directory
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

# Update requirements. This is a separate step so that if requirements.txt is unchanged, we do not reinstall everything.
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Remove packages used for installation
RUN apk del \
    gcc \
    libc-dev

# Copy the rest of the application code into the container
COPY . .

# Remove stale pidfiles
RUN rm -rf /*.pid

CMD /bin/sh
