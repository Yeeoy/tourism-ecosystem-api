from django.contrib.auth import (get_user_model, authenticate)
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


# 用户序列化器
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()  # 获取用户模型
        fields = ['email', 'password', 'name']  # 序列化的字段
        # 附加关键字参数
        extra_kwargs = {
            'password': {
                'write_only': True,  # 密码字段只写
                'min_length': 5  # 密码最小长度为5
            }
        }

    # 创建用户
    def create(self, validated_data):
        # 使用验证后的数据创建用户
        return get_user_model().objects.create_user(**validated_data)

    # 更新用户
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)  # 从验证数据中移除密码
        user = super().update(instance, validated_data)  # 更新用户的其他字段

        if password:
            user.set_password(password)  # 设置新密码
            user.save()  # 保存用户

        return user  # 返回更新后的用户


# 认证令牌序列化器
class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()  # 邮箱字段
    password = serializers.CharField(
        style={'input_type': 'password'},  # 密码字段的输入类型为密码
        trim_whitespace=False  # 不去除空白字符
    )

    # 验证方法
    def validate(self, attrs):
        email = attrs.get('email')  # 获取邮箱
        password = attrs.get('password')  # 获取密码

        user = authenticate(
            request=self.context.get('request'),  # 获取请求上下文
            username=email,  # 使用邮箱作为用户名
            password=password  # 使用提供的密码
        )

        if not user:
            # 无法使用提供的凭据进行认证
            msg = _('Unable to authenticate with provided credentials')
            # 抛出验证错误
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user  # 将用户添加到验证数据中
        return attrs  # 返回验证数据
