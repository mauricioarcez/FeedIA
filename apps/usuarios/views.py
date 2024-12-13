from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CommonUserRegistrationForm, BusinessUserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout as auth_logout
from django.contrib import messages


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

# Login para usuario común y negocio
def login_view(request):
    if request.method == 'POST':
        # Usar correo en lugar de username para negocio
        username_or_email = request.POST['username']  # Usuario o correo
        password = request.POST['password']

        # Validamos si es un negocio o un usuario común
        if '@' in username_or_email:  # Si contiene @ es un correo (usuario negocio)
            user = authenticate(request, email=username_or_email, password=password)
        else:  # Si no contiene @, se considera un usuario común con username
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)
            return redirect('usuarios:home')  # Redirige al inicio después del login exitoso
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

def register_business_user(request):
    """Vista para registrar un usuario de tipo negocio"""
    if request.method == 'POST':
        form = BusinessUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente después de registrar
            return redirect('usuarios:home')  # Redirige al home después de un registro exitoso
    else:
        form = BusinessUserRegistrationForm()

    return render(request, 'negocios/register_b.html', {'form': form})
