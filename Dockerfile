FROM joyzoursky/python-chromedriver:3.8

COPY . /app
WORKDIR /app

RUN export PATH=$PATH:/usr/lib/chromium-browser/

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /config

CMD [ "python3", "-u", "flathunt.py", "-c", "/config/config.yaml" ]