FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /visualizer
WORKDIR /visualizer
COPY requirements.txt /visualizer/
COPY config.json /visualizer/
RUN pip install -r requirements.txt