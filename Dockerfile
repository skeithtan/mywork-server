FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /mywork-code
COPY requirements.txt /mywork-code/
RUN pip install -r requirements.txt
COPY . /mywork-code/

