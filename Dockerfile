FROM mcr.microsoft.com/playwright/python:v1.25.0-focal
USER root

RUN mkdir -p /root/src
COPY src /root/src
WORKDIR /root/src

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
RUN playwright install --with-deps chromium

CMD [ "python", "bot.py" ]
