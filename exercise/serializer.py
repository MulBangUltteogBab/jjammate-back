from rest_framework import serializers


class GetExerciseGaugeSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class GetExerciseSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class GetMaximumTimeSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class GetSetCountSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class SetMaximumTimeSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    run = serializers.CharField(help_text='뜀뛰기시간', max_length=10, default="00:00")
    pushup = serializers.CharField(help_text='팔굽혀펴기개수', max_length=10, default="0")
    situp = serializers.CharField(help_text='윗몸일으키기개수', max_length=10, default="0")


class SetSetCountSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    setcount = serializers.JSONField(help_text='운동별 횟수', default={
        "운동A": 0,
        "운동B": 1
    })
