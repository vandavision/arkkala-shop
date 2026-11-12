FROM docker.arvancloud.ir/node:20-alpine

WORKDIR /app

COPY ./frontend/package.json ./frontend/package-lock.json* /app/

RUN npm install --registry=https://registry.npmmirror.com

COPY ./frontend /app/

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]