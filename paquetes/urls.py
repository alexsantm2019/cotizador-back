from django.urls import path
from . import views

urlpatterns = [  
    path('get_paquetes', views.get_paquetes, name='get_paquetes'),      
    path('paquete/<int:paquete_id>', views.get_paquete_by_id, name='get_paquete_by_id'),      
    path('create_paquete', views.create_paquete, name='create_paquete'),
    path('update_paquete/<int:paquete_id>', views.update_paquete, name='update_paquete'),
    path('delete_paquete/<int:paquete_id>', views.delete_paquete, name='delete_paquete'),
]