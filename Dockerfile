FROM ubuntu:20.04

SHELL ["/bin/bash", "-c"] 

ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get dist-upgrade \
    && apt-get install -y \
    python3.8 python3-distutils python3-pip python3-apt \
    build-essential \
    cmake \
    cython \
    libgsl-dev \
    libltdl-dev \
    libncurses-dev \
    libreadline-dev \
    python-all-dev \
    python-nose \
    openmpi-bin \
    libopenmpi-dev \
    libomp-dev \
    python3-mpi4py \
    wget

RUN echo alias python=python3 >>  ~/.bashrc
RUN source  ~/.bashrc

RUN wget https://github.com/nest/nest-simulator/archive/v2.20.0.tar.gz && \
    mkdir nest-build && \
    tar zxf v2.20.0.tar.gz && \
    cd  nest-build && \
    cmake   -Dwith-python=3 \
            -Dwith-mpi=ON \
            -Dwith-openmp=ON \
            -DCMAKE_INSTALL_PREFIX:PATH=/opt/nest/ ../nest-simulator-2.20.0 && \
    make && \
    make install

RUN source /opt/nest/bin/nest_vars.sh

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
RUN pip3 install --upgrade pip requests setuptools pipenv

COPY . /app

WORKDIR /app

RUN pip3 install --default-timeout=100 -r requirements.txt

EXPOSE 5000