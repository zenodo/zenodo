FROM node:latest
RUN npm install -g statsd git://github.com/markkimsal/statsd-elasticsearch-backend.git
COPY config.js /opt/statsd/config.js
COPY init-es.sh /init-es.sh
EXPOSE 8125/udp
CMD statsd /opt/statsd/config.js
