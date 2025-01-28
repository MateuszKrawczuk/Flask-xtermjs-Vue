FROM node:18-alpine as build-stage

ENV APP_HOME=/webapp

WORKDIR $APP_HOME
COPY package*.json ./
RUN npm install
RUN npm i -g serve
COPY . .

RUN npm run build


FROM nginx:stable-alpine
COPY --from=build-stage /webapp/dist /usr/share/nginx/html
COPY --from=build-stage /webapp/nginx.conf /etc/nginx/
COPY --from=build-stage /webapp/proxy_params /etc/nginx/

EXPOSE 9080
CMD ["nginx", "-g", "daemon off;"]