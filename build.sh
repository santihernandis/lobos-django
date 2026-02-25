#!/usr/bin/env bash
# Script de build para Render
# exit on error
set -o errexit

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "🗂️  Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "🗄️  Aplicando migraciones..."
python manage.py migrate

echo "✅ Build completado exitosamente!"
