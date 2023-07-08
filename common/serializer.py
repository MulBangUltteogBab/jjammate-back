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


class GetKcalStatusSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class GetNutritionStatusSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class GetExerciseSelectorSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class GetUnitListSerializer(serializers.Serializer):
    unique = serializers.CharField(help_text='부대이름', max_length=60)


class RegisterSuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='회원가입에 성공하셨습니다')


class RegisterFail1ResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='이미 존재하는 회원입니다.')


class KeyErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='받지 못한 데이터가 존재합니다.')


class ObjectDoesNotExistSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='데이터가 존재하지 않습니다.')


class LoginSuccessResponseSerializer(serializers.Serializer):
    token = serializers.CharField(help_text='토큰 전달')


class LoginErrorSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='회원 정보가 존재하지 않거나 비밀번호가 틀렸습니다.')


class NoDBErrorSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='데이터가 존재하지 않습니다.')


class ModifySuccessSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='수정 완료')


class ZeroDivisionErrorSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='키나 몸무게 중 0인 값이 있습니다.')


class GetMyInfoSuccessSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    username = serializers.CharField(help_text='성명', max_length=20, required=False)
    department = serializers.CharField(help_text='부서', max_length=60, required=False)
    sex = serializers.CharField(help_text='성별("m" or "f")', max_length=1, required=False)
    age = serializers.IntegerField(help_text='나이', max_value=32767, min_value=-32768, required=False)
    height = serializers.IntegerField(help_text='키', required=False)
    weight = serializers.IntegerField(help_text='몸무게', required=False)
    bmi = serializers.IntegerField(help_text='bmi', required=False)


class GetKcalStatusSuccessSerializer(serializers.Serializer):
    taken = serializers.FloatField(help_text="섭취량")
    burned = serializers.FloatField(help_text="소비량")
    remain = serializers.FloatField(help_text="잔여량")


class GetNutritionStatusSuccessSerializer(serializers.Serializer):
    taken = serializers.JSONField(help_text="탄단지섭취량")
    percent = serializers.JSONField(help_text="탄단지비율")
    total = serializers.JSONField(help_text="탄단지총량")


class GetExerciseSelectorSuccessSerializer(serializers.Serializer):
    days = serializers.IntegerField(help_text='운동날짜')


class GetUnitListSuccessSerializer(serializers.Serializer):
    units = serializers.ListField(help_text='검색할단어와유사한부대')
