# Base image with Python (choosing Ubuntu for compatibility)
FROM ubuntu:22.04

# Environment configurations
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_VERSION=3.13.0
ENV SQLITE_VERSION=3350000     # match for SQLite 3.35.0 as Makename expects (3 digit per segment)
ENV SQLITE_VERSION_STR=3.35.0

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        curl \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        ca-certificates \
        git \
        make \
        libffi-dev \
        liblzma-dev \
        xz-utils

# Build SQLite 3.35.0 (replace system libsqlite3)
RUN wget https://www.sqlite.org/2021/sqlite-autoconf-3350000.tar.gz && \
    tar xzf sqlite-autoconf-3350000.tar.gz && \
    cd sqlite-autoconf-3350000 && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    cd .. && \
    rm -rf sqlite-autoconf-3350000 sqlite-autoconf-3350000.tar.gz

# Install Python 3.13.0 from source
RUN wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz && \
    tar xzf Python-3.13.0.tgz && \
    cd Python-3.13.0 && \
    ./configure --enable-optimizations --with-ensurepip=install \
        --with-openssl \
        --enable-shared \
        --with-system-ffi \
        --with-system-sqlite \
        --prefix=/usr/local \
        CPPFLAGS="-I/usr/local/include" LDFLAGS="-L/usr/local/lib" && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    cd .. && \
    rm -rf Python-3.13.0 Python-3.13.0.tgz

# Upgrade pip and install poetry
RUN /usr/local/bin/python3.13 -m pip install --upgrade pip && \
    /usr/local/bin/python3.13 -m pip install poetry

# Set python3 default to 3.13
RUN ln -sf /usr/local/bin/python3.13 /usr/local/bin/python3 && \
    ln -sf /usr/local/bin/python3.13 /usr/bin/python3
