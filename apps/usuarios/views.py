from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CommonUserRegistrationForm, BusinessUserRegistrationForm
from django.contrib.auth import logout as auth_logout
from apps.encuestas.models import Encuesta
from django.contrib.auth import get_user_model

# ---------------------------------------------------------------------------------------------------------
def register(request):
    """Vista para registrar un usuario común"""
    if request.method == 'POST':
        form = CommonUserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el usuario
            return redirect('usuarios:login')  # Redirige a la página de login después del registro
    else:
        form = CommonUserRegistrationForm()  # Si no es POST, muestra un formulario vacío

    return render(request, 'usuarios/register_u.html', {'form': form})

# ---------------------------------------------------------------------------------------------------------

def login_view(request):
    """Vista para iniciar sesión, usando solo username"""
    if request.method == 'POST':
        username = request.POST['username']  # Solo se usa username para autenticarse
        password = request.POST['password']

        # Autenticación usando username
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  # Inicia sesión si las credenciales son correctas
            return redirect('usuarios:home')  # Redirige al home después de login exitoso
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'login.html')

# ---------------------------------------------------------------------------------------------------------

# Vista de logout
def logout_view(request):
    auth_logout(request)
    return redirect('usuarios:login')


# ---------------------------------------------------------------------------------------------------------
# Asegurarse de que la vista de inicio esté protegida
@login_required
def home_view(request):
    """Vista para la página de inicio de acuerdo al tipo de usuario"""
    if request.user.is_common_user():
        return render(request, 'usuarios/home_common.html')
    elif request.user.is_business_user():
        return render(request, 'negocios/home_business.html')
    return redirect('usuarios:login')  # Si no es común ni negocio, redirige al login


# ---------------------------------------------------------------------------------------------------------

def register_business(request):
    if request.method == 'POST':
        form = BusinessUserRegistrationForm(request.POST)
        if form.is_valid():
            # Crear el usuario pero no guardarlo todavía
            user = form.save(commit=False)
            
            # Establecer explícitamente el tipo como negocio
            user.user_type = 'business'
            
            # Normalizar la provincia
            user.provincia = form.cleaned_data['provincia'].lower().capitalize()
            
            # Guardar el usuario
            user.save()
            
            # Iniciar sesión automáticamente
            auth_login(request, user)
            
            return redirect('usuarios:home')
    else:
        form = BusinessUserRegistrationForm()

    return render(request, 'negocios/register_b.html', {'form': form})


# ---------------------------------------------------------------------------------------------------------

def home_common(request):
    CustomUser = get_user_model()
    
    # Obtener todos los negocios sin restricción de usuario
    total = CustomUser.objects.filter(
        user_type='business'
    ).count()
    
    context = {
        'total': total,
        'total_encuestas': Encuesta.objects.filter(
            usuario=request.user,
            encuesta_completada=True
        ).count()
    }
    
    return render(request, 'usuarios/home_common.html', context)