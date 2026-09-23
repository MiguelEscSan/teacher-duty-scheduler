FROM node:22-alpine AS build

WORKDIR /app

COPY Frontend/package*.json ./
RUN npm ci

COPY Frontend/ .
RUN npm run build -- --configuration production

FROM nginx:1.27-alpine

COPY Frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80
