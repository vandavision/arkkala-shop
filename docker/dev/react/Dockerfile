FROM node:20-alpine AS development

ENV NODE_ENV=development
WORKDIR /frontend

COPY frontend/package.json ./

RUN npm install

COPY ./frontend .

CMD ["npm", "run", "dev"]