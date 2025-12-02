# USA la imagen de Demisto que descargaste
FROM demisto/fastapi:0.118.0.5221545

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias adicionales
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de tu aplicación
COPY ./app ./app

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]