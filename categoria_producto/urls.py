from django.urls import path
from . import views
# from .views import get_usuarios

urlpatterns = [    
    path('get_categoria_producto', views.get_categoria_producto, name='get_categoria_producto'),        
    path('create_categoria_producto', views.create_categoria_producto, name='create_categoria_producto'),
    path('update_categoria_producto/<int:categoria_id>', views.update_categoria_producto, name='update_categoria_producto'),
    path('delete_categoria_producto/<int:categoria_id>', views.delete_categoria_producto, name='delete_categoria_producto'),
]