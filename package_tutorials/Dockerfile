#
# Dockerfile to add an R kernel in binder
# https://github.com/ahwillia/binder-Rkernel/blob/master/Dockerfile
#

# Pull base image.
FROM andrewosh/binder-base

MAINTAINER Stijn Van Hoey <stijn.vanhoey@inbo.be>

# Switch to root to install stuff
USER root
RUN apt-get update 

# Install R kernel to Jupyter notebook
RUN conda install -y -c r ipython-notebook r-irkernel

# Switch back to non-root user
USER main