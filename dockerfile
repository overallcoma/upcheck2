FROM alpine

LABEL maintainer="overallcoma <overallcoma@gmail.com>"

RUN apk upgrade --no-cache
RUN apk add --no-cache python3 py3-pip nginx bash
RUN pip3 install --upgrade pip
RUN pip3 install schedule speedtest-cli tzdata requests tweepy
RUN mkdir /db/
RUN mkdir /scripts/
COPY scripts/ /scripts/
COPY static/ /var/www/localhost/htdocs/

ENTRYPOINT /scripts/entrypoint.sh