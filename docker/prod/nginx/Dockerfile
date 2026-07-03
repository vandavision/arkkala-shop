FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM nginx:1.25-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY docker/prod/nginx/nginx.conf /etc/nginx/nginx.conf

COPY --from=frontend-builder /frontend/build /usr/share/nginx/html

RUN mkdir -p /app/staticfiles /app/mediafiles \
    && chown -R nginx:nginx /usr/share/nginx/html /app/staticfiles /app/mediafiles /var/cache/nginx /var/log/nginx /etc/nginx/conf.d

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]