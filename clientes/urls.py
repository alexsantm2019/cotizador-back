from django.urls import path
from . import views
# from .views import get_usuarios

urlpatterns = [    
    path('get_clientes', views.get_clientes, name='get_clientes'),    
    path('create_cliente', views.create_cliente, name='create_cliente'),
    path('update_cliente/<int:cliente_id>', views.update_cliente, name='update_cliente'),
    path('delete_cliente/<int:cliente_id>', views.delete_cliente, name='delete_cliente'),
]