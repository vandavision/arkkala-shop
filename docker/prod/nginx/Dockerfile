FROM node:20-alpine AS frontend-builder

WORKDIR /app

COPY ./frontend/package*.json ./
RUN npm ci

COPY ./frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ./docker/prod/nginx/nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /usr/share/nginx/html/main

COPY --from=frontend-builder /app/dist /usr/share/nginx/html/main

RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chmod -R 755 /usr/share/nginx/html