FROM node:20

WORKDIR /app

COPY package.json package-lock.json ./


RUN npm cache clean --force && \
    npm install --force

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]