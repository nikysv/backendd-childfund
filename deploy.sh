#!/bin/bash

# Script de inicialización para Render
echo "🚀 Iniciando despliegue en Render..."

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones de base de datos..."
flask db upgrade

echo "✅ Despliegue completado exitosamente!"
