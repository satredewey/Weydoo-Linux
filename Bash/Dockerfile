FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris

RUN apt update && \
    apt install -y sudo git curl tzdata && \
    rm -rf /var/lib/apt/lists/*