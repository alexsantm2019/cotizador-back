from django.urls import path
from . import views

urlpatterns = [    
    path('get_catalogo_by_grupo/<int:grupo>', views.get_catalogo_by_grupo, name='get_catalogo_by_grupo'),   
]