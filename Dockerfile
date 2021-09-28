FROM python:3.9
ENV PATH /usr/local/bin:$PATH
ADD gowcrawl /craw
WORKDIR /craw
RUN pip3 install -r requirements.txt
CMD python3 run.py
