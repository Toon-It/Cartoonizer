FROM tensorflow/tensorflow:1.15.2

LABEL maintainer="Kurian Benoy<kurian.bkk@gmail.com>"
ENV PYTHONBUFFERED 1

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

RUN apt-get install -y libgl1-mesa-glx
RUN python3 -m pip --no-cache-dir install --upgrade \
    pip \
    setuptools

ADD . /cartoonizer/
WORKDIR /cartoonizer
RUN pip -V
RUN pip install scikit-build
RUN pip install -r dev-requirements.txt
EXPOSE 5000

# ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
CMD ["python3", "main.py"]
