FROM node:6
RUN git config --global url."https://".insteadOf git://
RUN npm install -g statsd https://github.com/webcanvas/angular-schema-form-ckeditor.git
COPY config.js /opt/statsd/config.js
COPY init.sh /init.sh
EXPOSE 8125/udp
CMD statsd /opt/statsd/config.js
