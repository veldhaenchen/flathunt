FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ARG PIP_NO_CACHE_DIR=1

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

WORKDIR /usr/src/app
COPY . .

RUN pip install --upgrade pip && \
    pip install pipenv && \
    python --version; pip --version; pipenv --version

RUN pipenv requirements > requirements.txt
RUN pip install -r requirements.txt

CMD [ "python", "flathunt.py", "-c", "/config.yaml" ]