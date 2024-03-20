from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
   
    class Meta:
        model=User
        fields= ['id', 'username', 'email', 'is_vendor', 'is_active']
        
class SignupSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={"input_type":"password"}, write_only=True)
    class Meta:
        model=User
        fields=['username','email','password', 'password2', 'is_vendor']
        extra_kwargs={
            'password':{'write_only':True}
        }
    
    def save(self, **kwargs):
        user=User(
            username=self.validated_data['username'],
            email=self.validated_data['email']
        )
        password=self.validated_data['password']
        password2=self.validated_data['password2']
        if password !=password2:
            raise serializers.ValidationError({"error":"password do not match"})
        user.set_password(password)
        user.is_vendor=self.validated_data['is_vendor']
        # user.is_vendor= True
        user.save()
        return user


