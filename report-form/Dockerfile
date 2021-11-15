FROM node:16 as builder

WORKDIR /app

COPY package*.json ./
COPY src ./src

RUN npm ci && \
    npm run build

FROM nginx:latest as runner

COPY --from=builder /app/dist /usr/share/nginx/html

USER 1001

CMD ["nginx", "-g", "daemon off;"]
