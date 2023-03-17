FROM ubuntu:18.04

SHELL ["/bin/bash", "-c"] 

ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive

RUN echo alias python=python3 >>  ~/.bashrc
RUN echo alias pip=pip3 >>  ~/.bashrc
RUN source  ~/.bashrc

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y build-essential
RUN apt-get install -y cmake
RUN apt-get install -y cython
RUN apt-get install -y libgsl-dev
RUN apt-get install -y libltdl-dev
RUN apt-get install -y libncurses-dev
RUN apt-get install -y libreadline-dev
RUN apt-get install -y python-all-dev
RUN apt-get install -y openmpi-bin
RUN apt-get install -y libopenmpi-dev
RUN apt-get install -y python3-mpi4py
RUN apt-get install -y wget
RUN apt-get install -y git
RUN apt-get install -y python3-h5py

RUN apt-get install -y python3.6 python3-distutils python3-pip python3-apt
RUN ln -sfn /usr/bin/python3.6 /usr/bin/python

RUN pip3 install --user --upgrade cython

RUN mkdir -p /nest/build && \
    cd /nest/ && \
    wget https://github.com/nest/nest-simulator/archive/v2.18.0.tar.gz && \
    tar zxf v2.18.0.tar.gz

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10
RUN pip3 install --upgrade pip requests setuptools pipenv

RUN cd /nest/build && \
    cmake   -Dwith-python=3 \
            -Dwith-mpi=ON \
            -Dwith-openmp=ON \
            -DCMAKE_INSTALL_PREFIX:PATH=/nest/build/ ../nest-simulator-2.18.0 && \
    make && \
    make install

RUN cd /nest/ && \
    git clone https://github.com/alberto-antonietti/CerebNEST/
RUN mkdir -p /nest/cerebnest-build && cd /nest/cerebnest-build && cmake -Dwith-nest=/nest/build/bin/nest-config /nest/CerebNEST
RUN cd /nest/cerebnest-build && make && make install

COPY . /app

WORKDIR /app

RUN pip3 install --default-timeout=100 -r docker/requirements.txt
RUN chmod +x docker/run_gunicorn.sh

# EXPOSE 5000