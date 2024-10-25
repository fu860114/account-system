from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'token', 'role']  # 指定要序列化的欄位
        extra_kwargs = {
            'password': {'write_only': True},  # 確保密碼只在創建/更新時寫入，不能讀取
            'token': {'read_only': True},  # Token 只讀取，不會在創建或更新時提供
        }

    def create(self, validated_data):
        """
        在創建新使用者時自動處理密碼加密。
        """
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'Normal')  # 預設權限為 'Normal'
        )
        user.password = validated_data['password']
        user.save()  # 在模型中有 `save` 時會自動加密密碼
        return user

    def update(self, instance, validated_data):
        """
        更新時確保密碼字段加密。
        """
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        password = validated_data.get('password', None)
        if password:
            instance.password = password  # `save()` 方法會加密密碼

        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance
