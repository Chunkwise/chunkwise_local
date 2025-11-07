# .devcontainer/Dockerfile
# Debian slim base chosen for small image and compatibility with Codespaces.
FROM debian:12-slim

ARG PYTHON_VERSION=3.13.0
ARG SQLITE_VERSION=3350000
ARG SQLITE_TAG=3350000
ARG DEBIAN_FRONTEND=noninteractive

# set locale minimal
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH=/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH

# Create 'vscode' user with UID 1000 (Codespaces / local VS Code expects this)
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    wget \
    git \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libffi-dev \
    libncursesw5-dev \
    libgdbm-dev \
    liblzma-dev \
    tk-dev \
    pkg-config \
    openssl \
    procps \
    sudo \
    gnupg \
 && rm -rf /var/lib/apt/lists/*

# 1) Build and install SQLite 3.35.0 from source into /usr/local
WORKDIR /tmp
RUN SQLITE_VERSION_SHORT=3.35.0 \
 && SQLITE_TGZ=sqlite-autoconf-3350000.tar.gz \
 && wget -q "https://www.sqlite.org/2021/${SQLITE_TGZ}" -O /tmp/${SQLITE_TGZ} \
 && tar xzf ${SQLITE_TGZ} \
 && cd sqlite-autoconf-3350000 \
 && ./configure --prefix=/usr/local --disable-static --enable-shared \
 && make -j"$(nproc)" && make install \
 && cd /tmp && rm -rf /tmp/sqlite-autoconf-3350000 /tmp/${SQLITE_TGZ}

# Ensure ldconfig can find our custom sqlite
RUN echo "/usr/local/lib" > /etc/ld.so.conf.d/local-lib.conf && ldconfig

# 2) Build and install Python 3.13.0 from source and make it the system default python3
WORKDIR /tmp
RUN PY=3.13.0 \
 && PY_TGZ=Python-${PY}.tgz \
 && wget -q "https://www.python.org/ftp/python/${PY}/${PY_TGZ}" -O /tmp/${PY_TGZ} \
 && tar xzf ${PY_TGZ} \
 && cd Python-${PY} \
 # Make sure the build uses the headers/libraries installed in /usr/local (sqlite)
 && export CPPFLAGS="-I/usr/local/include" \
 && export LDFLAGS="-L/usr/local/lib" \
 && ./configure --enable-optimizations --with-ensurepip=install --enable-shared --prefix=/usr/local \
 && make -j"$(nproc)" \
 && make install \
 && cd /tmp && rm -rf /tmp/Python-${PY} /tmp/${PY_TGZ}

# Ensure the newly installed shared libs are discoverable
RUN ldconfig

# Symlink python3 and pip3 to /usr/local/bin
RUN ln -sf /usr/local/bin/python3 /usr/local/bin/python \
 && ln -sf /usr/local/bin/python3 /usr/local/bin/python3.13 \
 && ln -sf /usr/local/bin/pip3 /usr/local/bin/pip

# Create non-root vscode user (UID 1000) and give sudo without password (codespace convention)
RUN groupadd --gid ${USER_GID} ${USERNAME} \
 && useradd -s /bin/bash --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} \
 && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
 && chmod 0440 /etc/sudoers.d/${USERNAME}

# Install Poetry (official installer). This will put poetry in $HOME/.local/bin for the vscode user.
# We'll also create a global location for poetry so it's available for root and vscode:
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.7.0

RUN mkdir -p $POETRY_HOME \
 && curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_HOME python3 - \
 && ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry \
 && poetry --version

# Clean up apt caches (already removed earlier, but keep final cleanup)
RUN apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Ensure Poetry's bin is on PATH for the vscode user
ENV PATH=$POETRY_HOME/bin:/home/${USERNAME}/.local/bin:$PATH

# Default shell
SHELL ["/bin/bash", "-lc"]
