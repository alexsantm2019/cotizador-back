from django.urls import path
from . import views

urlpatterns = [    
    path('get_inventario', views.get_inventario, name='get_inventario'),    
    # path('get_productos_inventario', views.get_productos_inventario, name='get_productos_inventario'),    
    # path('create_producto', views.create_producto, name='create_producto'),
    # path('update_producto/<int:producto_id>', views.update_producto, name='update_producto'),
    # path('delete_producto/<int:producto_id>', views.delete_producto, name='delete_producto'),
]