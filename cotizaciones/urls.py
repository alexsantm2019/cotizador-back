from django.urls import path
from . import views

urlpatterns = [    
    path('get_cotizaciones', views.get_cotizaciones, name='get_cotizaciones'),    
    path('get_cotizacion_by_id/<int:cotizacion_id>', views.get_cotizacion_by_id, name='get_cotizacion_by_id'),
    path('get_cotizaciones_by_fecha/<int:year>/', views.get_cotizaciones_by_fecha, name='get_cotizaciones_by_fecha'),
    path('get_cotizaciones_by_fecha/<int:year>/<int:month>/', views.get_cotizaciones_by_fecha, name='get_cotizaciones_by_fecha'),
    path('create_cotizacion', views.create_cotizacion, name='create_cotizacion'),    
    path('update_cotizacion/<int:cotizacion_id>', views.update_cotizacion, name='update_cotizacion'),
    path('delete_cotizacion/<int:id>', views.delete_cotizacion, name='delete_cotizacion'),

    # Envio de PDF y Whatsapp:
    path('enviar_correo/<int:cotizacion_id>', views.enviar_correo, name='enviar_correo'),
    path('enviar_whatsapp/<int:cotizacion_id>', views.enviar_whatsapp, name='enviar_whatsapp'),
]