# syntax=docker/dockerfile:1

# Base devcontainer image (Ubuntu 22.04). You can swap to universal:2 if you need many preinstalled tools.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

USER root
ARG DEBIAN_FRONTEND=noninteractive

# Build dependencies for SQLite and Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl wget git build-essential make pkg-config \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libffi-dev \
    liblzma-dev tk-dev uuid-dev xz-utils libgdbm-dev libnss3-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------------------
# 1) Build and install SQLite 3.35.0 from source (goes to /usr/local)
# -------------------------------------------------------------------
ARG SQLITE_AUTOCONF=3350000
RUN wget -q https://www.sqlite.org/2021/sqlite-autoconf-${SQLITE_AUTOCONF}.tar.gz \
    && tar -xzf sqlite-autoconf-${SQLITE_AUTOCONF}.tar.gz \
    && cd sqlite-autoconf-${SQLITE_AUTOCONF} \
    && ./configure --prefix=/usr/local \
    && make -j"$(nproc)" \
    && make install \
    && cd .. \
    && rm -rf sqlite-autoconf-${SQLITE_AUTOCONF}* \
    && echo "/usr/local/lib" > /etc/ld.so.conf.d/usrlocal.conf \
    && ldconfig

# -------------------------------------------------------
# 2) Install pyenv system-wide and build Python with it
#    We make sure it links against /usr/local SQLite
# -------------------------------------------------------
# Use bash for the following RUNs (move earlier if you need bash sooner)
SHELL ["/bin/bash", "-lc"]

ENV PYENV_ROOT=/usr/local/pyenv
ENV PATH=${PYENV_ROOT}/bin:${PYENV_ROOT}/shims:$PATH
ENV CPPFLAGS="-I/usr/local/include"
ENV LDFLAGS="-L/usr/local/lib"
ENV PKG_CONFIG_PATH="/usr/local/lib/pkgconfig"

RUN git clone https://github.com/pyenv/pyenv.git ${PYENV_ROOT} \
 && mkdir -p ${PYENV_ROOT}/cache \
 && echo 'export PYENV_ROOT=/usr/local/pyenv' > /etc/profile.d/pyenv.sh \
 && echo 'export PATH=$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH' >> /etc/profile.d/pyenv.sh \
 && echo 'eval "$(pyenv init -)"' >> /etc/profile.d/pyenv.sh

# Build Python with pyenv ensuring env + init are active in the same RUN
RUN export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH" \
 && eval "$(pyenv init -)" \
 && pyenv install -v ${PYTHON_VERSION} \
 && pyenv global ${PYTHON_VERSION} \
 && pyenv rehash \
 && python -m pip install --upgrade pip setuptools wheel \
 && python - <<'PY'
import sqlite3, sys
print(sys.version)
print('linked sqlite:', sqlite3.sqlite_version)
PY

# -------------------------------------------------------
# 3) Install Poetry for the 'vscode' user
# -------------------------------------------------------
USER vscode
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc \
  && ~/.local/bin/poetry --version \
  && ~/.local/bin/poetry config virtualenvs.in-project true

# Done. The container default user will be 'vscode'.
