#!/usr/bin/env python
"""
Script de prueba para el sistema de configuración de roles
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lobos.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from juego.models import Sala, Jugador

def crear_sala_prueba():
    """Crea una sala de prueba con configuración personalizada"""
    
    # Crear sala
    sala = Sala.objects.create(codigo='TEST01')
    print(f"✅ Sala creada: {sala.codigo}")
    print(f"Configuración por defecto: {sala.configuracion_roles}")
    
    # Crear jugadores de prueba
    jugadores_data = [
        ('Alice', True),   # Líder
        ('Bob', False),
        ('Charlie', False),
        ('Diana', False),
        ('Eve', False),
    ]
    
    for nombre, es_lider in jugadores_data:
        Jugador.objects.create(
            session_id=f'session_{nombre.lower()}',
            nombre=nombre,
            sala=sala,
            es_lider=es_lider
        )
        print(f"✅ Jugador creado: {nombre} {'(Líder)' if es_lider else ''}")
    
    # Cambiar configuración de roles
    nueva_config = {
        'lobo': 1,
        'lobo_albino': 0,
        'lobo_padre': 0,
        'aldeano': 2,
        'arbol': 0,
        'cupido': 1,
        'bruja': 1,
        'nina_salvaje': 0,
        'cazador': 0,
        'vidente': 0,
    }
    
    sala.configuracion_roles = nueva_config
    sala.save()
    
    print(f"\n✅ Configuración actualizada:")
    total = sum(nueva_config.values())
    print(f"Total de roles: {total}")
    for rol, cantidad in nueva_config.items():
        if cantidad > 0:
            print(f"  - {rol.replace('_', ' ').title()}: {cantidad}")
    
    print(f"\n✅ Jugadores en la sala: {sala.jugadores.count()}")
    print(f"{'✅' if total <= sala.jugadores.count() else '❌'} Configuración válida: {total} roles para {sala.jugadores.count()} jugadores")
    
    return sala

def probar_reparto_roles():
    """Prueba el reparto de roles con configuración personalizada"""
    
    sala = Sala.objects.filter(codigo='TEST01').first()
    if not sala:
        print("❌ No existe la sala TEST01. Ejecuta crear_sala_prueba() primero.")
        return
    
    import random
    
    # Simular el reparto
    configuracion = sala.configuracion_roles
    roles_disponibles = []
    
    for rol, cantidad in configuracion.items():
        roles_disponibles.extend([rol] * cantidad)
    
    jugadores = list(sala.jugadores.all())
    num_jugadores = len(jugadores)
    
    # Rellenar con aldeanos si es necesario
    if num_jugadores > len(roles_disponibles):
        faltantes = num_jugadores - len(roles_disponibles)
        roles_disponibles.extend(['aldeano'] * faltantes)
        print(f"⚠️  Se añadieron {faltantes} aldeanos de relleno")
    
    # Barajar
    random.shuffle(roles_disponibles)
    
    # Asignar
    print(f"\n🎲 Repartiendo roles:")
    print("-" * 50)
    for i, jugador in enumerate(jugadores):
        jugador.rol = roles_disponibles[i]
        jugador.save()
        print(f"  {jugador.nombre:15} → {jugador.get_rol_display()}")
    print("-" * 50)
    
    print(f"\n✅ Roles repartidos exitosamente")

def limpiar_prueba():
    """Elimina la sala de prueba"""
    sala = Sala.objects.filter(codigo='TEST01').first()
    if sala:
        sala.delete()
        print("✅ Sala de prueba eliminada")
    else:
        print("❌ No existe la sala TEST01")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Prueba del sistema de configuración de roles')
    parser.add_argument('accion', 
                       choices=['crear', 'repartir', 'limpiar'],
                       help='Acción a realizar')
    
    args = parser.parse_args()
    
    if args.accion == 'crear':
        crear_sala_prueba()
    elif args.accion == 'repartir':
        probar_reparto_roles()
    elif args.accion == 'limpiar':
        limpiar_prueba()
