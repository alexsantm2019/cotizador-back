from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Llama al método validate del padre para obtener los tokens
        data = super().validate(attrs)
        
        # Se añaden mas datos a la api de respuesta
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['email'] = self.user.email

        if self.user.first_name and self.user.last_name:
            full_name = f"{self.user.first_name} {self.user.last_name}"        
        else:
            full_name = self.user.first_name  

        data['full_name'] = full_name
        
        return data