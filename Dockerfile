FROM ubuntu:18.04
ENTRYPOINT [ "/bin/bash", "-l", "-i", "-c" ]

# Set the mirror for `apt-get` to talk to.  This seems to have helps a situation where some packages below
# will sometimes work and sometimes give an IP Not Found error.  It's still not perfect.
RUN sed --in-place --regexp-extended "s/(\/\/)(archive\.ubuntu)/\us.\2/" /etc/apt/sources.list && \
    apt-get update && apt-get upgrade --yes

# delete all the apt list files since they're big and get stale quickly
RUN rm -rf /var/lib/apt/lists/*
# this forces "apt-get update" in dependent images, which is also good
# (see also https://bugs.launchpad.net/cloud-images/+bug/1699913)

# enable the universe
RUN sed -i 's/^#\s*\(deb.*universe\)$/\1/g' /etc/apt/sources.list

# make systemd-detect-virt return "docker"
# See: https://github.com/systemd/systemd/blob/aa0c34279ee40bce2f9681b496922dedbadfca19/src/basic/virt.c#L434
RUN mkdir -p /run/systemd && echo 'docker' > /run/systemd/container

# Clean cache and basic repository setup
RUN apt-get clean
RUN apt-get update && apt-get update --fix-missing
RUN apt-get install -y software-properties-common
RUN printf 'Y' | apt-get install apt-utils
RUN printf 'Y' | apt-get install vim
RUN apt-get update && export PATH
RUN apt-get install bc

# Sometimes this works and sometimes not also, retry.
# `libpython3.6-dev` is required for `python3-pip`
RUN apt-get update
RUN printf 'Y' | apt-get install libpython3.6-dev
RUN printf 'Y' | apt-get install python3-pip

# AWS Python SDK and CLI installations
RUN apt-get install -y unzip
RUN apt-get install -y curl
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

# Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Spacy
RUN pip3 install "https://github.com/huggingface/neuralcoref-models/releases/download/en_coref_sm-3.0.0/en_coref_sm-3.0.0.tar.gz"

# NLTK
RUN python3.6 -c "import nltk; nltk.download('stopwords');  \
    nltk.download('punkt'); \
    nltk.download('averaged_perceptron_tagger'); \
    nltk.download('maxent_ne_chunker'); \
    nltk.download('words'); \
    nltk.download('wordnet');"
RUN cp -r /root/nltk_data /usr/share/nltk_data

# Set python 3.6 as the default for the container
RUN ln -s /usr/bin/python3.6 /usr/bin/python

# Set root password
RUN echo "root:##rmarkbio%%" | chpasswd

# Install sudo
RUN apt-get update && apt-get -y install sudo

# overwrite this with 'CMD []' in a dependent Dockerfile
CMD ["/bin/bash"]

# Create and boot into a development user instead of working as root
RUN groupadd -r rmarkbio -g 901
RUN useradd -u 901 -r -g rmarkbio rmarkbio
RUN echo "rmarkbio:##rmarkbio%%" | chpasswd
RUN adduser rmarkbio sudo
RUN mkdir /home/rmarkbio
RUN mkdir /home/rmarkbio/project
RUN mkdir /home/rmarkbio/logs
RUN chown -R rmarkbio /home/rmarkbio
USER rmarkbio
WORKDIR /home/rmarkbio/project
