from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    password = serializers.CharField(help_text='비밀번호', max_length=20, required=False)
    # nickname = serializers.CharField(help_text='별칭', max_length=20, required=False)
    agreement = serializers.BooleanField(help_text='동의란 True/False')
    username = serializers.CharField(help_text='성명', max_length=20, required=False)
    department = serializers.CharField(help_text='부서', max_length=60, required=False)
    sex = serializers.CharField(help_text='성별("m" or "f")', max_length=1, required=False)
    age = serializers.IntegerField(help_text='나이', max_value=32767, min_value=-32768, required=False)
    height = serializers.IntegerField(help_text='키', required=False)
    weight = serializers.IntegerField(help_text='몸무게', required=False)


class LoginSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15, required=False)
    password = serializers.CharField(help_text='비밀번호', max_length=20, required=False)


class ModifySerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    password = serializers.CharField(help_text='비밀번호', max_length=20, required=False)
    username = serializers.CharField(help_text='성명', max_length=20, required=False)
    department = serializers.CharField(help_text='부서', max_length=60, required=False)
    height = serializers.IntegerField(help_text='키', required=False)
    weight = serializers.IntegerField(help_text='몸무게', required=False)


class GetMyInfoSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
