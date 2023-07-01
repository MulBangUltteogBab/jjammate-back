from rest_framework import serializers


class GetExerciseGaugeSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)

