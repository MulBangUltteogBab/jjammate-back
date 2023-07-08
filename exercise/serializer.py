from rest_framework import serializers


class GetExerciseSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class GetSetCountSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class SetSetCountSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    name = serializers.CharField(help_text='한 세트를 수행한 운동 이름', max_length=60)


class GetWeekRecordTimeSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class GetExerciseSuccessSerializer(serializers.Serializer):
    exercise = serializers.JSONField(help_text='운동별 횟수', default={
        "운동정보": "..."
    })


class SetRunCountSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    run = serializers.CharField(help_text='뜀뛰기', max_length=10)


class SetPushupCountSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    pushup = serializers.IntegerField(help_text='팔굽혀펴기')


class SetSitupCountSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    situp = serializers.IntegerField(help_text='윗몸일으키기')


class GetCountSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class SetExerciseSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    index = serializers.IntegerField(help_text='운동 아이디')