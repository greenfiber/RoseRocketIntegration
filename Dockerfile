# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM centos:latest
ARG CACHEBUST=1
# If you prefer miniconda:
#FROM continuumio/miniconda3

LABEL Name=phase1 Version=0.0.1
EXPOSE 6969
# RUN sudo su
RUN yum install -y \
    python-devel \
    python-setuptools \
    gcc-c++ \
    openssl-devel \
    bash
RUN git clone https://github.com/greenfiber/RoseRocketIntegration.git
WORKDIR /RoseRocketIntegration
RUN git checkout prod-dev
ADD . /RoseRocketIntegration
#install prereqs for pyodbc
RUN easy_install pip
RUN curl https://packages.microsoft.com/config/rhel/7/prod.repo > /etc/yum.repos.d/mssql-release.repo
RUN ACCEPT_EULA=Y yum install -y msodbcsql17
RUN ACCEPT_EULA=Y yum install -y mssql-tools
RUN yum install -y unixODBC-devel
RUN odbcinst -i -s -f ./dsn.txt -l
# Using pip:
RUN python -m pip install -r requirements.txt
ENTRYPOINT [ "python3" ]
CMD ["rrtosage.py","-u"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "phase1"]

# Using miniconda (make sure to replace 'myenv' w/ your environment name):
#RUN conda env create -f environment.yml
#CMD /bin/bash -c "source activate myenv && python3 -m phase1"
