from django.shortcuts import render

# Create your views here.
@login_required
def canjear_puntos(request):
    """Vista para canjear puntos"""
    if request.method == 'POST':
        negocio_id = request.POST.get('negocio')
        puntos_a_canjear = request.POST.get('puntos')
        
        # Aquí puedes agregar la lógica para procesar el canje de puntos
        messages.success(request, f'Has canjeado {puntos_a_canjear} puntos en el negocio seleccionado.')
        return redirect('encuestas:canjear')

    # Obtener la lista de negocios disponibles para el usuario
    negocios = CustomUser.objects.filter(user_type='business')
    return render(request, 'encuestas/canjear.html', {'negocios': negocios})

# ------------------------------------------------------------------------------------------------

@login_required
def administrar_canjear(request):
    """Vista para administrar los canjes"""
    if not request.user.is_business_user():
        messages.error(request, "Acceso denegado")
        return redirect('usuarios:home_common')

    canjes = Canje.objects.filter(negocio=request.user)

    if request.method == 'POST':
        form = CanjeForm(request.POST)
        if form.is_valid():
            canje = form.save(commit=False)
            canje.negocio = request.user  # Asignar el negocio actual
            canje.save()
            messages.success(request, "Canje creado exitosamente.")
            return redirect('encuestas:administrar_canjear')
    else:
        form = CanjeForm()

    return render(request, 'encuestas/administrar_canjear.html', {'canjes': canjes, 'form': form})