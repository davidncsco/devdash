# pull official base image
FROM node:17.8.0-alpine as build-frontend
WORKDIR /app
ARG API_URL=http://devrel-500
ARG VIRTUAL=false
ENV PATH /app/node_modules/.bin:$PATH
ENV REACT_APP_API_URL=${API_URL}
ENV REACT_APP_VIRTUAL_EVENT=${VIRTUAL}
ENV WDS_SOCKET_PORT 0
COPY package.json .

RUN npm install --silent

COPY ./ /app/

#RUN npm install react-scripts@5.0.0 -g --silent
RUN npm run build

# Build for production with nginx
FROM nginx:1.20.2-alpine

COPY --from=build-frontend /app/build/ /usr/share/nginx/html
COPY ./static/questions /usr/share/nginx/html/static/questions
#COPY ../backend/data/questions/ /usr/share/nginx/html/static