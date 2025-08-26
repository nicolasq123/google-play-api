from node:18.10.0

WORKDIR /app/gpapi

COPY . /app/gpapi/

RUN npm install
RUN npm install google-play-scraper@10.0.1

ENTRYPOINT ["npm", "start"]