# Tutorials

## Running the code online

These tutorials can be run online usinng the [binder](https://mybinder.org/) service and relying on the [rocker/binder](https://github.com/rocker-org/binder) R community managed Docker files. 

Check the following links to run the tutorials:

For the `rgbif` tutorial:

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/inbo/lifewatch-meeting-2018/master?filepath=package_tutorials%2Fsrc%2Fwaterinfo.ipynb)

For the `wateRinfo` tutorial:

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/inbo/lifewatch-meeting-2018/master?filepath=package_tutorials%2Fsrc%2FtutorialGBIF_occurrence_maps.ipynb)

## Running the code locally

These tutorials were setup as [Jupyter notebooks](https://jupyter.org/), providing with addition of an R kernel. in order to use R in Jupyter notebooks on your local machine, you need to install IRkernel and make it available to Jupyter by following steps as explained in this [link](https://irkernel.github.io/installation/).

An number of R dependencies are required to run the code itself apart from the highlighted packages (`rgbif` and `wateRinfo`). Following pacakages need to be installed as well:

For the `rgbif` tutorial:
```
install.packages(c('tidyverse', 'rgeos', 'rgdal', 'sp', 'ggmap', 'leaflet', 'assertthat', 'stringr', 'magrittr'))
```

For the `wateRinfo` tutorial:
```
install.packages(c('tidyverse','RColorBrewer'))
```

Both tutorials can be used as slideshow presentation, using the [RISE](https://github.com/damianavila/RISE) extension (also known as *live_reveal*). When provided, an additional menu item is provided to convert the tutorial in an interactive slideshow. 





