# referenced from https://github.com/ucsd-ets/datahub-example-notebook/blob/master/Dockerfile
# All requirements are directly taken from https://gitlab.com/dzhong1989/hvac-safety-control/-/blob/master/requirements.txt

# 1) choose base container
# generally use the most recent tag

# data science notebook
# https://hub.docker.com/repository/docker/ucsdets/datascience-notebook/tags
ARG BASE_CONTAINER=ucsdets/datascience-notebook:2020.2-stable

# scipy/machine learning (tensorflow)
# https://hub.docker.com/repository/docker/ucsdets/scipy-ml-notebook/tags
# ARG BASE_CONTAINER=ucsdets/scipy-ml-notebook:2020.2-stable

FROM $BASE_CONTAINER

LABEL maintainer="UC San Diego ITS/ETS <ets-consult@ucsd.edu>"

# 2) change to root to install packages
USER root

# RUN	apt-get install -y htop && apt-get install -y aria2c && apt-get install -y nmap && apt-get install -y traceroute 
# RUN	apt-get install -y htop aria2 nmap traceroute 

# 3) install packages
RUN pip install --no-cache-dir scipy arrow==0.15.8 certifi==2020.6.20 chardet==3.0.4 cycler==0.10.0 idna==2.10 kiwisolver==1.2.0 \
matplotlib==3.3.0 numpy==1.19.1 Pillow==7.2.0 pyparsing==2.4.7 python-dateutil==2.8.1 requests==2.24.0 six==1.15.0 urllib3==1.25.10

# Override command to disable running jupyter notebook at launch
# CMD ["/bin/bash"]
