# Tutorials

## Running the code online

These tutorials can be run online usinng the [binder](https://mybinder.org/) service and relying on the [rocker/binder](https://github.com/rocker-org/binder) R community managed Docker files. 

Click the binder link to run the tutorials (inside the `src` folder):

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/inbo/lifewatch-meeting-2018/master?filepath=package_tutorials%2Fsrc)


## Running the code locally

These tutorials (inside the `src` directory) were setup as [Jupyter notebooks](https://jupyter.org/), using an R kernel to enable R code within the notebook. To use notebooks yourself on your machine, we advice you to install [Anaconda](https://anaconda.org/), as eplained in the [jupyter installation guide](http://jupyter.readthedocs.io/en/latest/install.html#id4)

In order to use R in the Jupyter notebook as a kernel, you need to install the IRkernel and make it available to Jupyter by the steps explained in this [link](https://irkernel.github.io/installation/).

A number of R dependencies are required to run the code itself apart from the highlighted packages (`rgbif` and `wateRinfo`). Following pacakages need to be installed as well:

For the `rgbif` tutorial:
```
install.packages(c('tidyverse', 'rgeos', 'rgdal', 'sp', 'ggmap', 'leaflet', 'assertthat', 'stringr', 'magrittr'))
```

For the `wateRinfo` tutorial:
```
install.packages(c('tidyverse','RColorBrewer'))
```

**Note**: Both tutorials can be used as slideshow presentation, using the [RISE](https://github.com/damianavila/RISE) extension (also known as *live_reveal*). When provided, an additional menu item is provided to convert the tutorial in an interactive slideshow. However, this is not required to try out the code and was done purely for demonstration purposes.





