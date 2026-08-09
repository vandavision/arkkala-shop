# arkkala/docker/dev/nginx/Dockerfile
FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ./docker/dev/nginx/nginx.conf /etc/nginx/nginx.conf