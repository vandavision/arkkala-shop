FROM node:20-alpine

ENV CHROME_BIN=/usr/bin/chromium-browser \
    MEMORY_CACHE=1 \
    CACHE_TTL=259200

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk update && apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    dumb-init

WORKDIR /app

RUN npm init -y && \
    npm install prerender --registry=https://registry.npmmirror.com

COPY ./docker/prerender/server.js .

EXPOSE 3000

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["node", "server.js"]