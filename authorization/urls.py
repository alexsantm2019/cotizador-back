from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView  # Importa la vista personalizada

# urlpatterns = [
#     path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Usa la vista personalizada
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]

urlpatterns = [
    path('', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Ruta para obtener el token
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),   # Ruta para refrescar el token
]