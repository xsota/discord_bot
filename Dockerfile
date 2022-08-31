FROM python:3
USER root

RUN mkdir -p /root/src
COPY src /root/src
WORKDIR /root/src

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
RUN playwright install
RUN playwright install-deps
CMD [ "python", "bot.py" ]
