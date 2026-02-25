#!/usr/bin/env python
"""
Script de prueba para verificar la funcionalidad de compartir partida
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lobos.settings')
django.setup()

from juego.models import Sala, Jugador

def test_compartir():
    print("🧪 Probando funcionalidad de compartir partida...\n")
    
    # Limpiar datos de prueba anteriores
    Sala.objects.filter(codigo__startswith='TEST').delete()
    
    # 1. Crear una sala de prueba
    sala = Sala.objects.create(codigo='TEST99')
    print(f"✅ Sala creada: {sala.codigo}")
    
    # 2. Simular URL de compartir
    url_base = "http://localhost:8000"
    url_compartir = f"{url_base}/unirse/{sala.codigo}/"
    print(f"📋 URL para compartir: {url_compartir}")
    
    # 3. Simular que dos jugadores se unen
    jugador1 = Jugador.objects.create(
        session_id='test_session_001',
        nombre='Alice',
        sala=sala,
        es_lider=True
    )
    print(f"✅ Jugador 1 (Líder): {jugador1.nombre}")
    
    jugador2 = Jugador.objects.create(
        session_id='test_session_002',
        nombre='Bob',
        sala=sala,
        es_lider=False
    )
    print(f"✅ Jugador 2: {jugador2.nombre}")
    
    # 4. Verificar que están en la misma sala
    jugadores_sala = sala.jugadores.all()
    print(f"\n👥 Total jugadores en sala {sala.codigo}: {jugadores_sala.count()}")
    for j in jugadores_sala:
        rol_display = "👑 LÍDER" if j.es_lider else "Jugador"
        print(f"   - {j.nombre} ({rol_display})")
    
    # 5. Verificar configuración de roles
    print(f"\n⚙️ Configuración de roles:")
    config = sala.configuracion_roles
    if config:
        roles_activos = {k: v for k, v in config.items() if v > 0}
        for rol, cantidad in roles_activos.items():
            print(f"   - {rol.replace('_', ' ').title()}: {cantidad}")
        total = sum(config.values())
        print(f"\n📊 Total de roles configurados: {total}")
    else:
        print("   ⚠️ Sin configuración (se usará default)")
    
    print("\n✅ Prueba completada exitosamente!")
    print(f"\n💡 Para probar en el navegador:")
    print(f"   1. Inicia el servidor: daphne -b 0.0.0.0 -p 8000 lobos.asgi:application")
    print(f"   2. Abre: {url_compartir}")
    print(f"   3. Introduce tu nombre y serás redirigido automáticamente a la sala {sala.codigo}")

def limpiar():
    print("🧹 Limpiando datos de prueba...")
    count = Sala.objects.filter(codigo__startswith='TEST').delete()[0]
    print(f"✅ {count} registros eliminados")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'limpiar':
            limpiar()
        else:
            print("Uso: python test_compartir.py [limpiar]")
    else:
        test_compartir()
