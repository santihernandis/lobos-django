# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Jugador, Sala
import random
import json

def inicio(request):
    """Pantalla inicial simple que redirige al pre_lobby"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if not request.session.session_key:
            request.session.create()
        
        # Guardamos el nombre en la sesión temporalmente
        request.session['nombre_jugador'] = nombre
        
        # Si hay un código de sala en la sesión (viene de unirse_directo)
        codigo_sala = request.session.get('codigo_sala_pendiente')
        if codigo_sala:
            del request.session['codigo_sala_pendiente']
            return redirect('lobby', codigo_sala=codigo_sala)
        
        return redirect('pre_lobby')
    
    return render(request, 'juego/inicio.html')

def unirse_directo(request, codigo_sala):
    """Vista para unirse directamente a una sala mediante enlace"""
    # Verificar que la sala existe
    try:
        sala = Sala.objects.get(codigo=codigo_sala.upper())
    except Sala.DoesNotExist:
        return render(request, 'juego/inicio.html', {
            'error': f'La sala "{codigo_sala}" no existe o ha expirado.'
        })
    
    if not request.session.session_key:
        request.session.create()
    
    if request.method == 'POST':
        # El usuario envió su nombre desde el formulario
        nombre = request.POST.get('nombre')
        if nombre:
            # Crear o actualizar jugador
            jugador, created = Jugador.objects.get_or_create(
                session_id=request.session.session_key,
                defaults={
                    'nombre': nombre,
                    'sala': sala,
                    'es_lider': False
                }
            )
            if not created:
                jugador.nombre = nombre
                jugador.sala = sala
                jugador.es_lider = False
                jugador.save()
            
            # Guardar nombre en sesión
            request.session['nombre_jugador'] = nombre
            
            # Redirigir al lobby
            return redirect('lobby', codigo_sala=sala.codigo)
    
    # GET request
    # Verificar si el usuario ya tiene nombre
    nombre = request.session.get('nombre_jugador')
    if nombre:
        # Ya tiene nombre, crear/actualizar jugador y unirse directamente
        jugador, created = Jugador.objects.get_or_create(
            session_id=request.session.session_key,
            defaults={
                'nombre': nombre,
                'sala': sala,
                'es_lider': False
            }
        )
        if not created:
            jugador.nombre = nombre
            jugador.sala = sala
            jugador.es_lider = False
            jugador.save()
        
        return redirect('lobby', codigo_sala=sala.codigo)
    else:
        # No tiene nombre, mostrar formulario para que ingrese el nombre
        return render(request, 'juego/inicio.html', {
            'mensaje': f'Te estás uniendo a la sala {sala.codigo}'
        })

def pre_lobby(request):
    """Vista donde el usuario puede crear o unirse a una sala"""
    if not request.session.session_key:
        request.session.create()
    
    nombre = request.session.get('nombre_jugador')
    if not nombre:
        return redirect('inicio')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'crear':
            # Crear nueva sala
            codigo = Sala.generar_codigo()
            sala = Sala.objects.create(codigo=codigo)
            
            # Crear jugador como líder
            jugador, created = Jugador.objects.get_or_create(
                session_id=request.session.session_key,
                defaults={
                    'nombre': nombre,
                    'sala': sala,
                    'es_lider': True
                }
            )
            if not created:
                jugador.nombre = nombre
                jugador.sala = sala
                jugador.es_lider = True
                jugador.save()
            
            return redirect('lobby', codigo_sala=codigo)
        
        elif accion == 'unirse':
            # Unirse a sala existente
            codigo = request.POST.get('codigo', '').upper().strip()
            
            try:
                sala = Sala.objects.get(codigo=codigo)
                
                # Crear o actualizar jugador
                jugador, created = Jugador.objects.get_or_create(
                    session_id=request.session.session_key,
                    defaults={
                        'nombre': nombre,
                        'sala': sala,
                        'es_lider': False
                    }
                )
                if not created:
                    jugador.nombre = nombre
                    jugador.sala = sala
                    jugador.es_lider = False
                    jugador.save()
                
                return redirect('lobby', codigo_sala=codigo)
            
            except Sala.DoesNotExist:
                error = "Sala no encontrada. Verifica el código."
                return render(request, 'juego/pre_lobby.html', {'nombre': nombre, 'error': error})
    
    return render(request, 'juego/pre_lobby.html', {'nombre': nombre})

def lobby(request, codigo_sala):
    """Sala de espera de la partida"""
    session_key = request.session.session_key
    
    try:
        sala = get_object_or_404(Sala, codigo=codigo_sala)
        jugador_actual = Jugador.objects.get(session_id=session_key, sala=sala)
    except Jugador.DoesNotExist:
        return redirect('pre_lobby')

    # Obtenemos todos los jugadores de esta sala
    todos = sala.jugadores.all()
    
    # Asegurar que la configuración existe
    if not sala.configuracion_roles:
        sala.configuracion_roles = sala.get_configuracion_default()
        sala.save()
    
    # Calcular total de roles configurados
    total_roles = sum(sala.configuracion_roles.values()) if sala.configuracion_roles else 0
    
    # Generar URL completa para compartir
    url_compartir = request.build_absolute_uri(f'/unirse/{sala.codigo}/')
    
    context = {
        'jugador': jugador_actual,
        'todos_los_jugadores': todos,
        'sala': sala,
        'es_lider': jugador_actual.es_lider,
        'configuracion_roles': sala.configuracion_roles,
        'configuracion_roles_json': json.dumps(sala.configuracion_roles),
        'total_roles_configurados': total_roles,
        'url_compartir': url_compartir,
    }
    return render(request, 'juego/lobby.html', context)

def iniciar_partida(request, codigo_sala):
    """
    Vista para barajar y asignar roles a los jugadores de la sala.
    Solo puede ser llamada por el líder.
    El líder no recibe rol (es el narrador).
    Usa la configuración dinámica de roles de la sala.
    """
    session_key = request.session.session_key
    
    try:
        sala = get_object_or_404(Sala, codigo=codigo_sala)
        jugador_actual = Jugador.objects.get(session_id=session_key, sala=sala)
        
        # Verificar que sea el líder
        if not jugador_actual.es_lider:
            return redirect('lobby', codigo_sala=codigo_sala)
        
    except Jugador.DoesNotExist:
        return redirect('pre_lobby')
    
    # Construir "bolsa de roles" basada en la configuración
    roles_disponibles = []
    configuracion = sala.configuracion_roles or sala.get_configuracion_default()
    
    for rol, cantidad in configuracion.items():
        roles_disponibles.extend([rol] * cantidad)
    
    # Obtener todos los jugadores de la sala EXCEPTO el líder
    jugadores = list(sala.jugadores.exclude(es_lider=True))
    num_jugadores = len(jugadores)
    
    # Si hay más jugadores que roles configurados, rellenar con aldeanos
    if num_jugadores > len(roles_disponibles):
        faltantes = num_jugadores - len(roles_disponibles)
        roles_disponibles.extend(['aldeano'] * faltantes)
    
    # Barajar la lista de roles
    random.shuffle(roles_disponibles)
    
    # Asignar roles SOLO a los jugadores no-líderes y guardar
    for i, jugador in enumerate(jugadores):
        if i < len(roles_disponibles):
            jugador.rol = roles_disponibles[i]
        else:
            jugador.rol = 'aldeano'  # Fallback
        jugador.save()
    
    # El líder no recibe rol (queda como 'aldeano' por defecto pero será tratado como narrador)
    
    # Marcar la partida como iniciada
    sala.partida_iniciada = True
    sala.save()
    
    return redirect('lobby', codigo_sala=codigo_sala)

@require_POST
def guardar_configuracion_roles(request, codigo_sala):
    """
    Vista para guardar la configuración de roles.
    Solo puede ser llamada por el líder.
    """
    session_key = request.session.session_key
    
    try:
        sala = get_object_or_404(Sala, codigo=codigo_sala)
        jugador_actual = Jugador.objects.get(session_id=session_key, sala=sala)
        
        # Verificar que sea el líder
        if not jugador_actual.es_lider:
            return JsonResponse({'error': 'No tienes permisos'}, status=403)
        
        # No permitir cambios si la partida ya comenzó
        if sala.partida_iniciada:
            return JsonResponse({'error': 'La partida ya comenzó'}, status=400)
        
    except Jugador.DoesNotExist:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    # Obtener configuración del request
    try:
        data = json.loads(request.body)
        nueva_configuracion = data.get('configuracion', {})
        
        # Validar que todos los valores sean enteros positivos
        for rol, cantidad in nueva_configuracion.items():
            if not isinstance(cantidad, int) or cantidad < 0:
                return JsonResponse({'error': f'Valor inválido para {rol}'}, status=400)
        
        # Guardar configuración
        sala.configuracion_roles = nueva_configuracion
        sala.save()
        
        return JsonResponse({
            'success': True,
            'configuracion': sala.configuracion_roles
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)