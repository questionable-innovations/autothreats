FROM python:3.12-alpine 

# set work directory
WORKDIR /svgmapapi

# set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk update \
    && apk add gcc python3-dev g++ libc-dev make gdal gdal-dev py3-gdal py3-fiona proj proj-dev proj-util proj-data ethtool linux-headers musl-dev geos geos-dev

RUN pip install --upgrade pip

COPY . .

RUN chmod +x entrypoint.sh

ENV PROJ_DIR=/usr
ENV PROJ_LIBDIR=/usr
ENV PROJ_INCDIR=/usr/share/proj

# install dependencies
RUN python -m pip install --no-build-isolation -r requirements.txt
RUN python -m pip install prettymaps/

ENTRYPOINT ["/svgmapapi/entrypoint.sh"]
