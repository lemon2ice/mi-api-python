# USA la imagen de Demisto que descargaste
FROM demisto/fastapi:0.118.0.5221545

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para mysql-connector
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias adicionales
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de tu aplicación
COPY . .

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]