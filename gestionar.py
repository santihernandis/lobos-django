#!/usr/bin/env python
"""
Script de utilidad para gestionar el juego Los Lobos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lobos.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from juego.models import Jugador, Sala

def limpiar_todo():
    """Elimina todas las salas y jugadores de la base de datos"""
    num_jugadores = Jugador.objects.count()
    num_salas = Sala.objects.count()
    
    Jugador.objects.all().delete()
    Sala.objects.all().delete()
    
    print(f"✅ Se eliminaron {num_salas} sala(s) y {num_jugadores} jugador(es)")

def listar_salas():
    """Lista todas las salas activas"""
    salas = Sala.objects.all()
    if not salas:
        print("No hay salas en la base de datos")
        return
    
    print(f"\n📋 Salas Activas ({salas.count()}):")
    print("=" * 80)
    for sala in salas:
        estado = "🟢 Iniciada" if sala.partida_iniciada else "⏳ Esperando"
        num_jugadores = sala.jugadores.count()
        
        # Calcular total de roles configurados
        config = sala.configuracion_roles or {}
        total_roles = sum(config.values()) if config else 0
        
        print(f"Código: {sala.codigo} | Jugadores: {num_jugadores} | Estado: {estado}")
        print(f"Creada: {sala.creada_en.strftime('%d/%m/%Y %H:%M:%S')}")
        
        if config:
            print(f"Configuración de roles (Total: {total_roles}):")
            roles_activos = {k: v for k, v in config.items() if v > 0}
            if roles_activos:
                for rol, cant in roles_activos.items():
                    print(f"  - {rol.replace('_', ' ').title()}: {cant}")
            else:
                print("  (Sin roles configurados)")
        
        print("-" * 80)

def listar_jugadores(codigo_sala=None):
    """Lista todos los jugadores, opcionalmente filtrados por sala"""
    if codigo_sala:
        try:
            sala = Sala.objects.get(codigo=codigo_sala.upper())
            jugadores = sala.jugadores.all()
            print(f"\n📋 Jugadores de la Sala {sala.codigo} ({jugadores.count()}):")
        except Sala.DoesNotExist:
            print(f"❌ Error: No existe la sala con código {codigo_sala}")
            return
    else:
        jugadores = Jugador.objects.all()
        print(f"\n📋 Todos los Jugadores ({jugadores.count()}):")
    
    if not jugadores:
        print("No hay jugadores")
        return
    
    print("-" * 80)
    for j in jugadores:
        estado = "💚 Vivo" if j.esta_vivo else "💀 Muerto"
        lider = "👑" if j.es_lider else "  "
        sala_info = j.sala.codigo if j.sala else "Sin sala"
        print(f"{lider} {j.nombre:20} | Sala: {sala_info:8} | Rol: {j.get_rol_display():15} | {estado}")
    print("-" * 80)

def resetear_sala(codigo_sala):
    """Resetea una sala específica (roles y estado)"""
    try:
        sala = Sala.objects.get(codigo=codigo_sala.upper())
        sala.partida_iniciada = False
        sala.save()
        
        jugadores = sala.jugadores.all()
        count = jugadores.update(rol='aldeano', esta_vivo=True)
        
        print(f"✅ Sala {sala.codigo} reseteada:")
        print(f"   - Partida marcada como no iniciada")
        print(f"   - {count} jugador(es) reseteados a aldeano")
    except Sala.DoesNotExist:
        print(f"❌ Error: No existe la sala con código {codigo_sala}")

def eliminar_sala(codigo_sala):
    """Elimina una sala específica y todos sus jugadores"""
    try:
        sala = Sala.objects.get(codigo=codigo_sala.upper())
        num_jugadores = sala.jugadores.count()
        sala.delete()
        print(f"✅ Sala {codigo_sala} eliminada (incluyendo {num_jugadores} jugador(es))")
    except Sala.DoesNotExist:
        print(f"❌ Error: No existe la sala con código {codigo_sala}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestión del juego Los Lobos')
    parser.add_argument('accion', 
                       choices=['limpiar', 'listar_salas', 'listar_jugadores', 'resetear', 'eliminar'],
                       help='Acción a realizar')
    parser.add_argument('codigo', nargs='?', help='Código de la sala (para acciones específicas)')
    
    args = parser.parse_args()
    
    if args.accion == 'limpiar':
        confirmar = input("⚠️  ¿Estás seguro de eliminar TODAS las salas y jugadores? (s/n): ")
        if confirmar.lower() == 's':
            limpiar_todo()
    
    elif args.accion == 'listar_salas':
        listar_salas()
    
    elif args.accion == 'listar_jugadores':
        listar_jugadores(args.codigo)
    
    elif args.accion == 'resetear':
        if not args.codigo:
            print("❌ Error: Debes proporcionar el código de la sala")
            print("Uso: python gestionar.py resetear ABC123")
        else:
            resetear_sala(args.codigo)
    
    elif args.accion == 'eliminar':
        if not args.codigo:
            print("❌ Error: Debes proporcionar el código de la sala")
            print("Uso: python gestionar.py eliminar ABC123")
        else:
            confirmar = input(f"⚠️  ¿Estás seguro de eliminar la sala {args.codigo}? (s/n): ")
            if confirmar.lower() == 's':
                eliminar_sala(args.codigo)
