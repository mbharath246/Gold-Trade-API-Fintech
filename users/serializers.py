from rest_framework import serializers
from users.models import CustomUser



class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'name',
            'email',
            'dob',
            'created_at',
            'password',
            'confirm_password'
        ]


    def create(self, obj):
        password = obj.pop('password',None)
        confirmed_password = obj.pop('confirm_password',None)
        user = self.Meta.model(**obj)
        if password != confirmed_password:
            raise serializers.ValidationError('Passwords Not Matched')
        if password is None:
            raise serializers.ValidationError('Passwords cannot be empty.')
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        confirmed_password = validated_data.pop('confirm_password',None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password and password != confirmed_password:
            raise serializers.ValidationError('Passwords Not Matched')
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.pop('email',None)
        password = attrs.pop('password', None)
        confirmed_password = attrs.pop('confirm_password',None)

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError('Invalid Email')
        
        if password and password != confirmed_password:
            raise serializers.ValidationError('Passwords Not Matched')
        if password:
            user.set_password(password)
        user.save()
        return user