# Usa la imagen oficial de Python como base
FROM python:3.8-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requisitos a la imagen
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del directorio actual al directorio de trabajo en la imagen
COPY . .

# Expone el puerto 5000 en la imagen
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
