# --- ETAPA 1: Construcción (Build) ---
# Usamos una imagen de Node para compilar el proyecto
FROM node:18-alpine as build-stage

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos primero los archivos de dependencias para aprovechar la caché de Docker
COPY package*.json ./

# Instalamos las dependencias
RUN npm install

# Copiamos el resto del código fuente
COPY . .

# Ejecutamos el comando de build (esto crea la carpeta /dist)
RUN npm run build

# --- ETAPA 2: Producción (Nginx) ---
# Usamos una imagen ligera de Nginx para servir los archivos
FROM nginx:alpine as production-stage

# 1. Copiamos la "build" de Vue
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 2. ¡NUEVO! Copiamos nuestra configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]