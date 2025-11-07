# syntax=docker/dockerfile:1

# Base devcontainer image (Ubuntu 22.04).
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
ARG SQLITE_AUTOCONF=3350000     # 3.35.0 => 3350000
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
# -------------------------------------------------------
ENV PYENV_ROOT=/usr/local/pyenv
ENV PATH=${PYENV_ROOT}/bin:${PYENV_ROOT}/shims:$PATH

RUN git clone https://github.com/pyenv/pyenv.git ${PYENV_ROOT} \
    && mkdir -p ${PYENV_ROOT}/cache \
    && echo 'export PYENV_ROOT=/usr/local/pyenv' > /etc/profile.d/pyenv.sh \
    && echo 'export PATH=$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH' >> /etc/profile.d/pyenv.sh \
    && echo 'eval "$(pyenv init -)"' >> /etc/profile.d/pyenv.sh

# Choose the Python version here
ARG PYTHON_VERSION=3.13.0

# Ensure Python build finds the /usr/local SQLite headers/libs
ENV CPPFLAGS="-I/usr/local/include"
ENV LDFLAGS="-L/usr/local/lib"
ENV PKG_CONFIG_PATH="/usr/local/lib/pkgconfig"

# Build Python and verify the linked SQLite version
RUN bash -lc "pyenv install -v ${PYTHON_VERSION} \
  && pyenv global ${PYTHON_VERSION} \
  && python -m pip install --upgrade pip setuptools wheel \
  && python - <<'PY'\nimport sqlite3, sys; print(sys.version); print('linked sqlite:', sqlite3.sqlite_version)\nPY"

# Use bash as default shell for subsequent RUNs
SHELL ["/bin/bash", "-lc"]

# -------------------------------------------------------
# 3) Install Poetry
# -------------------------------------------------------
USER vscode
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc \
  && ~/.local/bin/poetry --version \
  && ~/.local/bin/poetry config virtualenvs.in-project true