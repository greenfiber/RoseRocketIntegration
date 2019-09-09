# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM jfloff/alpine-python
ARG CACHEBUST=1
# If you prefer miniconda:
#FROM continuumio/miniconda3

LABEL Name=phase1 Version=0.0.1
EXPOSE 6969
RUN git clone https://github.com/greenfiber/RoseRocketIntegration.git
WORKDIR /RoseRocketIntegration
RUN git checkout prod-dev
ADD . /RoseRocketIntegration

# Using pip:
RUN python3 -m pip install -r requirements.txt
ENTRYPOINT [ "python3" ]
CMD ["rrtosage.py","-u"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "phase1"]

# Using miniconda (make sure to replace 'myenv' w/ your environment name):
#RUN conda env create -f environment.yml
#CMD /bin/bash -c "source activate myenv && python3 -m phase1"
