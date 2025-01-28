FROM oven/bun:alpine AS build-stage

ENV APP_HOME=/webapp

WORKDIR $APP_HOME
COPY package*.json ./
RUN bun install
COPY . ./
RUN bun run build


FROM nginx:stable-alpine
COPY --from=build-stage /webapp/dist /usr/share/nginx/html
COPY --from=build-stage /webapp/nginx.conf /etc/nginx/
COPY --from=build-stage /webapp/proxy_params /etc/nginx/

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]