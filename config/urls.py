from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

def criar_admin_temporario(request):
    token = request.GET.get('token')

    if token != 'galera-fc-admin-2026':
        return HttpResponse('Acesso negado.', status=403)

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='ghfs.tc@gmail.com',
            password='Admin@123456'
        )

        return HttpResponse('Superusuário criado com sucesso.')

    return HttpResponse('Superusuário já existe.')

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='financeiro/login.html'
        ),
        name='login'
    ),
    
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    
    path('', include('financeiro.urls')),
]
