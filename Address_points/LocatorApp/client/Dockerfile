FROM node:18
LABEL MAINTAINER="Brian H Wilson <bwilson@clatsopcounty.gov>"

RUN [ "npm", "install", "http-server", "-g" ]

EXPOSE 8080/tcp

WORKDIR /app

# Used for starting up the server
COPY package.json .

WORKDIR /app/public 

# The bundled app lives here
COPY public/ .

ENTRYPOINT [ "http-server", "/app/public" ]
