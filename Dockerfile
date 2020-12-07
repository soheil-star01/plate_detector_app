FROM ubuntu:latest

ENV DEBIAN_FRONTEND noninteractive
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y update
RUN apt-get install -y build-essential python3.6 python3-pip python3-dev
RUN pip3 -q install pip --upgrade

RUN apt-get update && apt-get install -y \ 
    libglib2.0-0 \
    libopencv-dev \ 
    libjpeg-dev \ 
    libpng-dev \ 
    libtiff-dev \ 
    libgtk2.0-dev \ 
    libatlas-base-dev \
    qt5-default \
    libvtk6-dev \ 
    zlib1g-dev 

RUN mkdir src
WORKDIR src/
COPY . .

RUN pip3 install -r requirements.txt
RUN sudo pip install git+https://github.com/myhub/tr.git@master
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
