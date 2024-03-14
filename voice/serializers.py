from .models import *
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

class UserSerializers(serializers.ModelSerializer):  # 登录专用返回人员usertype的
    usertype = serializers.CharField(
        source="get_usertype_display", read_only=True)

    class Meta:
        model = User
        fields = '__all__'

class RegisterSerializers(serializers.ModelSerializer):
    username = serializers.CharField(required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all())])
    repassword = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password', 'phone', 'repassword']

    def validate(self, attrs):
        if attrs['password'] != attrs['repassword']:
            raise serializers.ValidationError('两次密码不一致')
        del attrs['repassword']
        return attrs
    
class VoiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Voicefile
        fields = '__all__'

class UsersoundSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserSound
        fields = '__all__'