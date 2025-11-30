from django.urls import path
from . import views

urlpatterns = [    
    path('get_catalogo_by_grupo/<int:grupo>', views.get_catalogo_by_grupo, name='get_catalogo_by_grupo'),   
    path('get_catalogo_by_nombre/<str:nombre>', views.get_catalogo_by_nombre, name='get_catalogo_by_nombre'),       
    path('get_catalogos/', views.get_catalogos, name='get_catalogos'),
    path('get_catalogos_activos/', views.get_catalogos_activos, name='get_catalogos_activos'),
    path('delete_catalogo/<int:id>/', views.eliminar_catalogo, name='eliminar_catalogo'),    
    path('create_catalogo/', views.crear_catalogo, name='eliminar_catalogo'),
    path('update_catalogo/<int:catalogo_id>', views.update_catalogo, name='update_catalogo'),
]