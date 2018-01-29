#
# see https://github.com/binder-examples/dockerfile-r/blob/master/Dockerfile

FROM rocker/binder:3.4.2

## Copies your repo files into the Docker Container
USER root
COPY . ${HOME}
RUN chown -R ${NB_USER} ${HOME}

## Become normal user again
USER ${NB_USER}

## Run an install.R script, if it exists.
RUN if [ -f install.R ]; then R --quiet -f install.R; fi

#Custom installs for these tutorials
RUN R --quiet -e "devtools::install_github('inbo/wateRinfo')"
RUN R --quiet -e "install.packages(c('ggmap', 'leaflet'))"
RUN R --quiet -e "install.packages('rgbif')"
