FROM amd64/debian:latest
ADD . /CAFQA
WORKDIR /CAFQA

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y wget
RUN mkdir -p ~/miniconda3
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
RUN bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
RUN rm ~/miniconda3/miniconda.sh
RUN ~/miniconda3/bin/conda init bash