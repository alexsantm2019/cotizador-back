"""
URL configuration for cotizador_mundieventos_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from authorization.views import MyTokenObtainPairView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/categoria_producto/', include('categoria_producto.urls')),
    path('api/productos/', include('productos.urls')),
    path('api/catalogos/', include('catalogos.urls')),
    path('api/paquetes/', include('paquetes.urls')),
    path('api/clientes/', include('clientes.urls')),
    path('api/cotizaciones/', include('cotizaciones.urls')),
    path('api/inventario/', include('inventario.urls')),

    # Autenticacion v1.0 (jwt by default)
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Autenticacion v2.0 (jwt Para incluir el id del usuario ("auth"), llamando a la vista en autorhization) 
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Autenticacion v3.0 (jwt Para incluir el id del usuario ("auth"))    
    # path('api/token/', include('authorization.urls')),    
]
