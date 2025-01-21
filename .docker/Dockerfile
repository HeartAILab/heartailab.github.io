# start with official ruby docker image as base
FROM ruby:3.1.2

# set working directory within container
WORKDIR /usr/src/app

# pull in ruby (jekyll) and python (cite process) package info
COPY Gemfile Gemfile.lock _cite/requirements.txt ./

# install ruby packages
RUN VERSION=$(grep -A 1 'BUNDLED WITH' Gemfile.lock | tail -n 1 | xargs); \
    gem install bundler --version ${VERSION} && \
    bundle _${VERSION}_ install

# install python + system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    # Add required dependencies for Chromium
    chromium \
    # 1) Install Xvfb
    xvfb \
    # We often need extra libraries for Chrome
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    libpangocairo-1.0-0 fonts-liberation

# install python packages
RUN python3 -m pip install --no-cache-dir --upgrade --requirement requirements.txt

# install python package for listening for file changes
RUN pip install "watchdog[watchmedo]==3.0.0"

RUN pip install tweepy

# ports used by jekyll
EXPOSE 4000
EXPOSE 35729

# run jekyll and cite process
COPY .docker/entrypoint.sh /var
RUN chmod +x /var/entrypoint.sh

# Wrap the entrypoint with xvfb-run so that
# anything inside the container has a DISPLAY
# and can render in “headful” mode.
CMD [ "xvfb-run", "--auto-servernum", "--server-args=-screen 0 1280x1024x24", "/var/entrypoint.sh" ]
