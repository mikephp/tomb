FROM ubuntu:14.04

# Update software repository
ADD sources.list /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get update -y

# Create user dirlt with password dirlt
RUN useradd -G adm,root -m -s /bin/bash -d /home/dirlt2 dirlt2
RUN useradd -G adm,root -m -s /bin/bash -d /home/dirlt dirlt
RUN echo dirlt:dirlt | chpasswd
RUN apt-get install -y sudo
RUN echo "dirlt ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/dirlt
RUN echo "Defaults:dirlt  !requiretty" >> /etc/sudoers.d/dirlt
RUN chmod 0440 /etc/sudoers.d/dirlt

# Set up ssh access
RUN apt-get install -y openssh-server
RUN mkdir -p /var/run/sshd

# Install basic packages
USER root
RUN apt-get install -y git python vim lsof

# Set up basic env
USER dirlt
WORKDIR /home/dirlt
RUN mkdir -p .ssh
RUN echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCmWyPUgH07g2B9pbdNtf3LWWd6meQT5K8yk9VBIZbHjhU1SyP0SQxbbAAebAT2K2DmIsdBmR3nfHWhpGuZyxds/mhnOrX2rnBmdUVEPKKPHWohmfTN11FsPfTFGY9AzTOuVTTI1gcoVLrmXyLJay4uPa2kXtF2TtvqyeQB0iVTPmk9afJIYPQ9r2o++wLucay94zS3/9DenCsSoZw2Mt2NAz+25h7765cJqWjMRkL6BinZD+r9IBe/7y1hmj86fSQHzxVyE+AR/gdNsl38TujLPibfU0pOho4oGfONvtnT4/ZT2C8/8H2FdrL6cY5ww1JKptSQxl65vinnyTEMMwsH dirlt@ubuntu" >> .ssh/authorized_keys

USER root
