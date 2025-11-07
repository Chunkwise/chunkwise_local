FROM ubuntu:22.04

ARG PYTHON_VERSION=3.13.0
ARG SQLITE_VERSION=3350000
ARG SQLITE_VERSION_STR=3.35.0

ENV DEBIAN_FRONTEND=noninteractive

# Basic dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        curl \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libffi-dev \
        liblzma-dev \
        xz-utils \
        git \
        ca-certificates \
        make \
        sudo

# Build and install SQLite 3.35.0
RUN wget https://www.sqlite.org/2021/sqlite-autoconf-${SQLITE_VERSION}.tar.gz && \
    tar xzf sqlite-autoconf-${SQLITE_VERSION}.tar.gz && \
    cd sqlite-autoconf-${SQLITE_VERSION} && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    cd .. && \
    rm -rf sqlite-autoconf-${SQLITE_VERSION} sqlite-autoconf-${SQLITE_VERSION}.tar.gz

# Build and install Python 3.13.0 (using updated SQLite)
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
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
    rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tgz

# Ensure correct symlink
RUN ln -sf /usr/local/bin/python3.13 /usr/bin/python3 && \
    ln -sf /usr/local/bin/python3.13 /usr/local/bin/python3

# Upgrade pip and install poetry
RUN python3 --version && python3 -m pip install --upgrade pip && python3 -m pip install poetry

# Verify python and sqlite linkage
RUN python3 -c "import sqlite3, sys; print(sys.version); print('linked sqlite:', sqlite3.sqlite_version)"
