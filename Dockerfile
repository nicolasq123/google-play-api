from node:18.10.0

WORKDIR /app/gpapi

COPY . /app/gpapi/

RUN npm install

ENTRYPOINT ["npm", "start"]