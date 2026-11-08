# Front-end do JogoTeca: compila com Node e serve os arquivos prontos com Nginx.
FROM node:22-alpine AS compilar
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Endereço da API como o NAVEGADOR enxerga (é gravado no código na compilação)
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=compilar /app/dist /usr/share/nginx/html
EXPOSE 80
