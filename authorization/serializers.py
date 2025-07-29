from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Llama al método validate del padre para obtener los tokens
        data = super().validate(attrs)
        
        # Agrega el ID del usuario a la respuesta
        data['user_id'] = self.user.id
        
        return data