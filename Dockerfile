# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM ubuntu:18.04
ARG CACHEBUST=1
# If you prefer miniconda:
#FROM continuumio/miniconda3

LABEL Name=phase1 Version=0.0.1
EXPOSE 6969
# RUN sudo su
#grab msft stuff
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add --no-tty -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
#install python stuff
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip git
#clone git repo for app
RUN git clone https://github.com/greenfiber/RoseRocketIntegration.git
WORKDIR /RoseRocketIntegration
#checkout proper branch
RUN git checkout prod-dev
# ADD . /RoseRocketIntegration
# RUN scl enable rh-python37 bash
#install prereqs for pyodbc

RUN ACCEPT_EULA=Y apt install -y msodbcsql17
RUN ACCEPT_EULA=Y apt install -y mssql-tools
RUN yum install -y unixODBC-devel
RUN odbcinst -i -s -f ./dsn.txt -l
# Using pip:
RUN pip3 install -r requirements.txt
ENTRYPOINT [ "python3" ]
CMD ["rrtosage.py","-u"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "phase1"]

# Using miniconda (make sure to replace 'myenv' w/ your environment name):
#RUN conda env create -f environment.yml
#CMD /bin/bash -c "source activate myenv && python3 -m phase1"
