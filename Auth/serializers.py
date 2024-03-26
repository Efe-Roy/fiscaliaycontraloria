from rest_framework import serializers
from .models import User
from store.models import Address
from store.serializers import AddressSerializer

class UserSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
   
    class Meta:
        model=User
        fields= ['id', 'username', 'email', 'is_vendor', 'is_rider', 'is_client', 'is_active', 'acc_balance', 'image', 'address']

    def get_address(self, obj):
        user_addresses = Address.objects.filter(user=obj)
        serializer = AddressSerializer(instance=user_addresses, many=True)
        return serializer.data
        
class SignupSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={"input_type":"password"}, write_only=True)
    class Meta:
        model=User
        fields=['username','email','password', 'password2', 'is_vendor', 'is_rider', 'is_client']
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
        user.is_rider=self.validated_data['is_rider']
        user.is_client=self.validated_data['is_client']
        # user.is_vendor= True
        user.save()
        return user


