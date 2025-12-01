FROM ubuntu:20.04

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y \
    clang \
    curl \
    g++ \
    gcc \
    git \
    libclang-dev \
    libssl-dev \
    llvm \
    locales \
    make \
    pkg-config \
    sudo \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
RUN useradd -m -s /bin/bash ubuntu
RUN echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu
ENV LANG="en_US.UTF-8" \
    PATH="/home/ubuntu/local/bin:/home/ubuntu/.cargo/bin:/home/ubuntu/.local/bin:${PATH}"

COPY --chown=ubuntu:ubuntu cmake-3.31.9-linux-x86_64 local
COPY --chown=ubuntu:ubuntu ninja local/bin
COPY --chown=ubuntu:ubuntu Python-3.14.0 Python-3.14.0
RUN cd Python-3.14.0 \
 && ./configure --prefix=/home/ubuntu/local \
 && make -j \
 && make install \
 && cd .. \
 && rm -rf Python-3.14.0
RUN pip3 install toml

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
  | sh -s -- -y -q --default-toolchain nightly-2025-06-23-x86_64-unknown-linux-gnu

RUN git clone https://github.com/Medowhill/c2rust \
 && cd c2rust \
 && git checkout tractor-0.21.0 \
 && cargo build --release -Z sparse-registry \
 && ln -s ~/c2rust/target/release/c2rust-transpile ~/local/bin

RUN git clone https://github.com/kaist-plrg/crat \
 && cd crat \
 && git checkout 7e7d744 \
 && cd deps_crate \
 && cargo build \
 && cd .. \
 && cargo build --release --bin crat \
 && ln -s ~/crat/crat ~/local/bin

RUN cd crat \
 && git checkout master \
 && git pull \
 && git checkout 8d0b27e \
 && cargo build --release --bin crat

RUN pip3 install libclang

COPY --chown=ubuntu:ubuntu Test-Corpus Test-Corpus
WORKDIR /home/ubuntu/Test-Corpus

COPY --chown=ubuntu:ubuntu fixes.patch .
RUN git checkout 96ce4c7 \
 && git apply fixes.patch \
 && rm fixes.patch \
 && cd deployment/scripts/github-actions \
 && rm run-tests.pyz \
 && python3 -m zipapp . -m "runtests.__main__:main" -p "/usr/bin/env python3" -o run-tests.pyz

COPY --chown=ubuntu:ubuntu \
     add_link_args.py \
     cdylib.py \
     find_fns.py \
     filter_files.py \
     get_target.py \
     translate.sh \
     translate_all.py \
     ./
