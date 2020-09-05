FROM python:3.7

LABEL maintainer="Kurian Benoy<kurian.bkk@gmail.com>"
  ENV PYTHONBUFFERED 1
  ADD . /cartoonizer/
  WORKDIR /cartoonizer

  RUN python3 -m pip install -r requirements.txt
  EXPOSE 5000

  CMD ["python3", "/cartoonizer/main.py"]
