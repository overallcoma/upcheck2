FROM nginx:alpine

LABEL maintainer="overallcoma <overallcoma@gmail.com>"

RUN apk upgrade --no-cache
RUN apk add --no-cache python3 py3-pip nginx bash
RUN pip3 install --upgrade pip
RUN pip3 install schedule speedtest-cli tzdata requests tweepy
RUN mkdir /db/
RUN mkdir /scripts/
COPY scripts/ /scripts/
RUN mv /scripts/start-upcheck2.sh /docker-entrypoint.d/start-upcheck2.sh
RUN chmod +x /docker-entrypoint.d/start-upcheck2.sh
COPY static/ /usr/share/nginx/html/