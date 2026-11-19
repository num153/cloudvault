# Dockerfile mẫu cho Frontend (Node.js / React / Next.js)
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN if [ -f package.json ]; then npm install; fi

COPY . .

EXPOSE 3000

CMD ["sh", "-c", "if [ -f package.json ]; then npm run dev -- --host 0.0.0.0; else echo 'Frontend source code not mounted/found' && tail -f /dev/null; fi"]
