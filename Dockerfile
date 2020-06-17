FROM gcr.io/google-appengine/python
RUN virtualenv /env -p python3.7

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH


RUN apt-get update && \
    apt-get install -y default-jre
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt


ADD . /files-uploader
WORKDIR /files-uploader
ENV PYTHONPATH /files-uploader
EXPOSE 8888
CMD python main.py