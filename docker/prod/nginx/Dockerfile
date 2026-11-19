FROM docker.arvancloud.ir/nginx:1.27-alpine

RUN rm -f /etc/nginx/conf.d/default.conf

COPY ./docker/prod/nginx/nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /usr/share/nginx/html/main /var/www/certbot \
    && chown -R nginx:nginx /usr/share/nginx/html /var/www/certbot